#!/usr/bin/env python3
"""Main orchestrator: analyze a local project and publish contextual GitHub history."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from typing import Any, Callable, Dict, List, Optional

from github import Github
from rich.console import Console

from core.achievement_unlocker import AchievementUnlocker, SUPPORTED_BADGES
from core.ai_analyzer import AIAnalyzer
from core.ai_client import AIClient
from core.commit_planner import CommitPlanner
from core.github_publisher import GitHubPublisher
from core.history_builder import HistoryBuilder
from core.project_scanner import ProjectScanner

ProgressCallback = Optional[Callable[[str, int], None]]


class ProjectBot:
    """Analyze an existing local project and publish real contextual history to GitHub."""

    def __init__(
        self,
        github_token: str,
        openai_api_key: Optional[str] = None,
        openai_model: Optional[str] = None,
    ):
        self.github_token = github_token
        self.ai_client = AIClient(api_key=openai_api_key, model=openai_model)
        self.analyzer = AIAnalyzer(self.ai_client)
        self.planner = CommitPlanner(self.ai_client)
        self.console = Console()
        self._owner_identity: Optional[Dict[str, str]] = None

    def get_owner_identity(self) -> Dict[str, str]:
        """Resolve the authenticated GitHub user identity used for contribution counting."""
        if self._owner_identity:
            return self._owner_identity

        gh = Github(self.github_token)
        user = gh.get_user()
        # Prefer public email; fall back to the stable noreply address GitHub always accepts
        email = user.email or f"{user.id}+{user.login}@users.noreply.github.com"
        self._owner_identity = {
            "name": user.name or user.login,
            "email": email,
            "login": user.login,
            "id": str(user.id),
            "noreply": f"{user.id}+{user.login}@users.noreply.github.com",
        }
        return self._owner_identity

    def _team_for_contribution_graph(
        self,
        team_members: List[Dict[str, Any]],
        count_on_graph: bool,
    ) -> List[Dict[str, Any]]:
        """
        GitHub contribution graph matches commits by AUTHOR EMAIL.

        Fake team emails (e.g. alex.rivera@codepulse.dev) never count on your graph.
        When count_on_graph=True, keep display names but force every author email to
        the authenticated GitHub user's noreply address.
        """
        if not count_on_graph:
            return team_members

        owner = self.get_owner_identity()
        remapped = []
        for member in team_members:
            remapped.append(
                {
                    **member,
                    # Keep persona names for realistic history, but use YOUR email
                    "email": owner["noreply"],
                    "github_login": owner["login"],
                    "counts_on_graph": True,
                }
            )

        if not remapped:
            remapped = [
                {
                    "name": owner["name"],
                    "email": owner["noreply"],
                    "role": "Owner",
                    "activity_level": "high",
                    "counts_on_graph": True,
                }
            ]

        self.console.print(
            f"[green]Contribution graph mode ON[/green] — "
            f"commits will use {owner['noreply']} so they count for @{owner['login']}"
        )
        return remapped

    def publish_project(
        self,
        project_path: str,
        repo_name: str,
        config: Optional[Dict[str, Any]] = None,
        progress_callback: ProgressCallback = None,
    ) -> Dict[str, Any]:
        config = config or {}
        work_dir = tempfile.mkdtemp(prefix="repo-bot-work-")

        try:
            return self._run_pipeline(project_path, repo_name, config, work_dir, progress_callback)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def _run_pipeline(
        self,
        project_path: str,
        repo_name: str,
        config: Dict[str, Any],
        work_dir: str,
        progress_callback: ProgressCallback,
    ) -> Dict[str, Any]:
        def update(status: str, progress: int) -> None:
            if progress_callback:
                progress_callback(status, progress)

        update("scanning_project", 5)
        self.console.print(f"[bold blue]Scanning project:[/bold blue] {project_path}")
        snapshot = ProjectScanner(project_path).scan()
        self.console.print(
            f"[green]Found {snapshot.file_count} files, language: {snapshot.detected_language}[/green]"
        )

        update("analyzing_project", 15)
        self.console.print("[blue]Running deep project analysis...[/blue]")
        analysis = self.analyzer.analyze(snapshot)
        if self.ai_client.available:
            self.console.print("[green]AI analysis complete[/green]")
        else:
            self.console.print("[yellow]OPENAI_API_KEY not set — using local analysis fallback[/yellow]")

        num_commits = config.get("num_commits", 50)
        days_back = config.get("days_back", 90)
        raw_team = config.get("team_members") or self._default_team()
        count_on_graph = config.get("count_on_contribution_graph", True)
        team_members = self._team_for_contribution_graph(raw_team, count_on_graph)
        commit_style = config.get("commit_style", "conventional")

        update("planning_commits", 30)
        self.console.print(f"[blue]Planning {num_commits} contextual commits...[/blue]")
        commits = self.planner.plan(
            snapshot=snapshot,
            analysis=analysis,
            num_commits=num_commits,
            days_back=days_back,
            team_members=team_members,
            commit_style=commit_style,
        )
        self.console.print(f"[green]Planned {len(commits)} commits from real project files[/green]")

        update("building_history", 45)
        repo_build_dir = os.path.join(work_dir, "repo")
        os.makedirs(repo_build_dir, exist_ok=True)

        all_files = ProjectScanner(project_path).list_all_sync_files()
        self.console.print(
            f"[blue]Publishing full project tree: {len(all_files)} files "
            f"(analysis used {snapshot.file_count})[/blue]"
        )

        history_builder = HistoryBuilder(project_path, all_project_files=all_files)
        build_result = history_builder.build(
            commits=commits,
            work_dir=repo_build_dir,
            progress_callback=progress_callback,
        )
        repo_dir = build_result["repo_dir"]
        commits_applied = build_result["commits_applied"]
        self.console.print(
            f"[green]Applied {commits_applied} commits; "
            f"synced {build_result.get('files_synced', 0)} project files[/green]"
        )

        description = config.get("description") or analysis.get("summary", f"Professional {snapshot.name} project")
        private = config.get("private", True)
        create_issues = config.get("create_issues", False)
        create_prs = config.get("create_prs", False)
        unlock_achievements = config.get("unlock_achievements", False)

        if create_issues or create_prs:
            self.console.print(
                "[yellow]Note:[/yellow] GitHub cannot backdate Issue/PR creation times. "
                "Only commit history can have real past timestamps."
            )

        publisher = GitHubPublisher(self.github_token, team_members=team_members)
        result = publisher.publish(
            repo_dir=repo_dir,
            repo_name=repo_name,
            description=description,
            private=private,
            analysis=analysis,
            create_issues=create_issues,
            create_prs=create_prs,
            progress_callback=progress_callback,
        )

        achievement_result = None
        if unlock_achievements:
            update("unlocking_achievements", 94)
            self.console.print("[blue]Unlocking GitHub profile achievements...[/blue]")
            unlocker = AchievementUnlocker(self.github_token, team_members=team_members)
            achievement_result = unlocker.unlock(
                repo_name=repo_name,
                badges=config.get("achievement_badges") or SUPPORTED_BADGES,
                pull_shark_count=int(config.get("pull_shark_count", 16)),
                pair_count=int(config.get("pair_count", 10)),
                reaction_rounds=int(config.get("reaction_rounds", 20)),
                delay_seconds=float(config.get("achievement_delay", 2.0)),
                progress_callback=progress_callback,
            )

        update("completed", 100)

        return {
            "success": True,
            "repository_url": result["repository_url"],
            "commits_created": commits_applied,
            "commits_planned": len(commits),
            "issues_created": result["issues_created"],
            "pull_requests_created": result["pull_requests_created"],
            "pull_requests_merged": result.get("pull_requests_merged", 0),
            "achievements": achievement_result,
            "analysis_summary": analysis.get("summary", ""),
            "language": snapshot.detected_language,
            "frameworks": snapshot.detected_frameworks,
            "ai_powered": self.ai_client.available,
        }

    @staticmethod
    def _default_team() -> list:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        if os.path.exists(config_path):
            with open(config_path, encoding="utf-8") as handle:
                data = json.load(handle)
                return data.get("developers", [])
        return [
            {
                "name": "Alex Rivera",
                "email": "alex.rivera@codepulse.dev",
                "role": "Senior Full Stack Developer",
                "activity_level": "high",
            }
        ]

    def validate_project_path(self, project_path: str) -> Dict[str, Any]:
        """Validate and preview a project path without publishing."""
        scanner = ProjectScanner(project_path)
        snapshot = scanner.scan()
        return {
            "valid": True,
            "name": snapshot.name,
            "path": snapshot.root,
            "file_count": snapshot.file_count,
            "language": snapshot.detected_language,
            "frameworks": snapshot.detected_frameworks,
            "dependencies": snapshot.dependencies[:20],
            "sample_files": [f.path for f in snapshot.files[:15]],
        }
