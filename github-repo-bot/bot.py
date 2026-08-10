#!/usr/bin/env python3
"""
GitHub Repository Enhancement Bot
Analyze existing local projects with AI and publish contextual history to GitHub.
"""

from __future__ import annotations

import json
import os
import sys

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from core.achievement_unlocker import AchievementUnlocker, SUPPORTED_BADGES, describe_badges
from core.project_bot import ProjectBot

load_dotenv()
console = Console()


def _load_team(config_path: str) -> list:
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as handle:
            return json.load(handle).get("developers", [])
    return []


@click.command()
@click.option("--project-path", type=click.Path(exists=True, file_okay=False), help="Local project folder to analyze and push")
@click.option("--repo-name", default="", help="GitHub repository name to create/use")
@click.option("--commits", default=50, show_default=True, help="Number of commits to generate")
@click.option("--days-back", default=90, show_default=True, help="Days of commit history")
@click.option("--private", is_flag=True, default=True, show_default=True, help="Create private repository")
@click.option("--public", is_flag=True, help="Create public repository (overrides --private)")
@click.option("--create-issues/--no-create-issues", default=False, show_default=True, help="Create issues NOW (cannot backdate)")
@click.option("--create-prs/--no-create-prs", default=False, show_default=True, help="Create PRs NOW (cannot backdate; commits inside can be historical)")
@click.option("--count-on-graph/--no-count-on-graph", default=True, show_default=True, help="Use your GitHub email so commits appear on the contribution graph")
@click.option("--unlock-achievements/--no-unlock-achievements", default=False, show_default=True, help="Optional badge farming (not real project history)")
@click.option("--achievements-only", is_flag=True, help="Only run badge unlocker on an existing repo")
@click.option("--pull-shark-count", default=16, show_default=True, help="Merged PRs for Pull Shark")
@click.option("--pair-count", default=10, show_default=True, help="Coauthored merges for Pair Extraordinaire")
@click.option("--description", default="", help="Repository description (auto-detected if empty)")
@click.option("--config", "config_path", default="config.json", show_default=True, help="Team/config JSON file")
@click.option("--github-token", envvar="GITHUB_TOKEN", help="GitHub token")
@click.option("--openai-api-key", envvar="OPENAI_API_KEY", help="OpenAI API key for deep analysis")
@click.option("--validate-only", is_flag=True, help="Only scan and validate the project path")
@click.option("--list-badges", is_flag=True, help="List supported achievement badges and exit")
def main(
    project_path,
    repo_name,
    commits,
    days_back,
    private,
    public,
    create_issues,
    create_prs,
    count_on_graph,
    unlock_achievements,
    achievements_only,
    pull_shark_count,
    pair_count,
    description,
    config_path,
    github_token,
    openai_api_key,
    validate_only,
    list_badges,
):
    """Analyze a local project with AI and publish real contextual history to GitHub."""

    console.print(
        Panel.fit(
            "[bold blue]GitHub Repository Enhancement Bot[/bold blue]\n"
            "[dim]AI-powered analysis + multi-badge achievement unlocker[/dim]",
            border_style="blue",
        )
    )

    if list_badges:
        for badge in describe_badges():
            console.print(f"[cyan]{badge['id']}[/cyan] — {badge['name']}: {badge['description']}")
        return

    if not repo_name:
        console.print("[red]Error: --repo-name is required[/red]")
        sys.exit(1)

    if achievements_only:
        if not github_token:
            console.print("[red]Error: GitHub token required[/red]")
            sys.exit(1)
        unlocker = AchievementUnlocker(github_token, team_members=_load_team(config_path))
        result = unlocker.unlock(
            repo_name=repo_name,
            badges=SUPPORTED_BADGES,
            pull_shark_count=pull_shark_count,
            pair_count=pair_count,
        )
        console.print_json(data=result)
        return

    if validate_only:
        if not project_path:
            console.print("[red]--project-path is required for validate-only[/red]")
            sys.exit(1)
        bot = ProjectBot(github_token=github_token or "dummy", openai_api_key=openai_api_key)
        preview = bot.validate_project_path(project_path)
        console.print_json(data=preview)
        return

    if not project_path:
        console.print("[red]Error: --project-path is required (or use --achievements-only)[/red]")
        sys.exit(1)

    if not github_token:
        console.print("[red]Error: GitHub token required. Set GITHUB_TOKEN or use --github-token[/red]")
        sys.exit(1)

    if not openai_api_key:
        console.print(
            "[yellow]Warning: OPENAI_API_KEY not set. Using local analysis fallback.[/yellow]\n"
            "[dim]Set OPENAI_API_KEY for deep AI-powered commit/issue/PR generation.[/dim]"
        )

    bot = ProjectBot(github_token=github_token, openai_api_key=openai_api_key)

    config = {
        "num_commits": commits,
        "days_back": days_back,
        "private": False if public else private,
        "create_issues": create_issues,
        "create_prs": create_prs,
        "unlock_achievements": unlock_achievements,
        "count_on_contribution_graph": count_on_graph,
        "pull_shark_count": pull_shark_count,
        "pair_count": pair_count,
        "achievement_badges": SUPPORTED_BADGES,
        "description": description,
        "team_members": _load_team(config_path),
    }

    try:
        result = bot.publish_project(
            project_path=project_path,
            repo_name=repo_name,
            config=config,
        )

        console.print(f"\n[bold green]Success![/bold green] {result['repository_url']}")
        console.print(f"Commits: {result['commits_created']}")
        console.print(f"Issues: {result['issues_created']}")
        console.print(f"Pull requests: {result['pull_requests_created']}")
        if result.get("achievements"):
            console.print(f"Achievements: {', '.join(result['achievements'].get('earned') or []) or 'none'}")
        console.print(f"AI powered: {result['ai_powered']}")
        if result.get("analysis_summary"):
            console.print(f"\n[dim]{result['analysis_summary']}[/dim]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        sys.exit(1)
    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
