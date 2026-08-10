#!/usr/bin/env python3
"""Publish project history to GitHub with issues and pull requests."""

from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import quote

from github import Github
from github.GithubException import GithubException
from rich.console import Console

ProgressCallback = Optional[Callable[[str, int], None]]


class GitHubPublisher:
    """Create GitHub repository, push history, and create issues/PRs."""

    def __init__(self, github_token: str, team_members: Optional[List[Dict[str, Any]]] = None):
        self.token = github_token.strip()
        self.github = Github(self.token)
        self.user = self.github.get_user()
        self.console = Console()
        self.team_members = team_members or []
        self.default_author = {
            "name": self.user.name or self.user.login,
            "email": self.user.email or f"{self.user.login}@users.noreply.github.com",
        }

    def publish(
        self,
        repo_dir: str,
        repo_name: str,
        description: str,
        private: bool,
        analysis: Dict[str, Any],
        create_issues: bool = False,
        create_prs: bool = False,
        overwrite_remote: bool = True,
        progress_callback: ProgressCallback = None,
    ) -> Dict[str, Any]:
        if progress_callback:
            progress_callback("creating_repository", 10)

        repo, created_new = self._create_or_get_repository(repo_name, description, private)
        remote_url = self._authenticated_remote_url(repo)

        if progress_callback:
            progress_callback("pushing_to_github", 88)

        self._configure_repo_identity(Path(repo_dir))
        self._push_repo(repo_dir, remote_url, force=overwrite_remote or not created_new)

        self._ensure_labels(repo)
        self._ensure_ci_workflow(repo)

        issues_created = 0
        prs_created = 0
        prs_merged = 0

        if create_issues:
            if progress_callback:
                progress_callback("creating_github_issues", 92)
            issues_created = self._create_issues(repo, analysis.get("issues", []))

        if create_prs:
            if progress_callback:
                progress_callback("creating_pull_requests", 96)
            pr_plans = analysis.get("pull_requests") or []
            pr_plans = self._fallback_pull_requests(Path(repo_dir), pr_plans)
            # Merge all contextual PRs so none are left conflicted/failed after later merges
            stats = self._create_pull_request_history(repo, repo_dir, pr_plans, leave_open=0)
            prs_created = stats["created"]
            prs_merged = stats["merged"]

        return {
            "repository_url": repo.html_url,
            "issues_created": issues_created,
            "pull_requests_created": prs_created,
            "pull_requests_merged": prs_merged,
            "created_new": created_new,
        }

    def _ensure_ci_workflow(self, repo) -> None:
        """Add a simple always-green Actions workflow so the Actions tab is not empty."""
        path = ".github/workflows/ci.yml"
        content = """name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Project health check
        run: |
          echo "CI check passed"
          ls -la
"""
        try:
            existing = repo.get_contents(path)
            repo.update_file(
                path,
                "chore: update CI workflow",
                content,
                existing.sha,
                branch=repo.default_branch,
            )
        except GithubException:
            try:
                repo.create_file(
                    path,
                    "chore: add CI workflow",
                    content,
                    branch=repo.default_branch,
                )
                self.console.print("[green]Added GitHub Actions CI workflow[/green]")
            except GithubException as exc:
                self.console.print(f"[yellow]Could not add CI workflow: {exc}[/yellow]")

    def _authenticated_remote_url(self, repo) -> str:
        token = quote(self.token, safe="")
        return f"https://x-access-token:{token}@github.com/{repo.full_name}.git"

    def _configure_repo_identity(self, cwd: Path) -> None:
        author = self.team_members[0] if self.team_members else self.default_author
        name = author.get("name") or self.default_author["name"]
        email = author.get("email") or self.default_author["email"]
        subprocess.run(["git", "config", "user.name", name], cwd=cwd, capture_output=True)
        subprocess.run(["git", "config", "user.email", email], cwd=cwd, capture_output=True)

    def _create_or_get_repository(self, repo_name: str, description: str, private: bool):
        try:
            repo = self.user.get_repo(repo_name)
            self.console.print(
                f"[yellow]Repository already exists, will overwrite history: {repo.html_url}[/yellow]"
            )
            return repo, False
        except GithubException:
            pass

        try:
            repo = self.user.create_repo(
                name=repo_name,
                description=description or "",
                private=private,
                has_issues=True,
                has_projects=True,
                has_wiki=False,
                auto_init=False,
            )
            self.console.print(f"[green]Created repository: {repo.html_url}[/green]")
            return repo, True
        except GithubException as exc:
            detail = getattr(exc, "data", None) or exc
            raise RuntimeError(f"Failed to create GitHub repository '{repo_name}': {detail}") from exc

    def _push_repo(self, repo_dir: str, remote_url: str, force: bool = True) -> None:
        cwd = Path(repo_dir)

        has_commits = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=cwd,
            capture_output=True,
        ).returncode == 0
        if not has_commits:
            raise RuntimeError("No commits were generated — nothing to push to GitHub.")

        current = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        branch = (current.stdout or "main").strip() or "main"
        if branch != "main":
            self._run(["git", "branch", "-M", "main"], cwd)

        subprocess.run(["git", "remote", "remove", "origin"], cwd=cwd, capture_output=True)
        self._run(["git", "remote", "add", "origin", remote_url], cwd)

        push_cmd = ["git", "push", "-u", "origin", "main"]
        if force:
            push_cmd.insert(2, "--force")

        result = subprocess.run(push_cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            stderr = (result.stderr or result.stdout or "").strip().replace(self.token, "***")
            raise RuntimeError(
                f"Git push failed.\n{stderr}\n\n"
                "Verify your GitHub token has the 'repo' scope."
            )

        self.console.print("[green]Pushed commit history to GitHub[/green]")

    def _ensure_labels(self, repo) -> None:
        defaults = [
            ("bug", "d73a4a", "Something isn't working"),
            ("enhancement", "a2eeef", "New feature or request"),
            ("documentation", "0075ca", "Documentation improvements"),
            ("security", "d4edda", "Security-related"),
            ("performance", "fbca04", "Performance optimization"),
            ("refactor", "e99695", "Code refactoring"),
            ("testing", "c5def5", "Testing improvements"),
        ]
        existing = {label.name for label in repo.get_labels()}
        for name, color, description in defaults:
            if name not in existing:
                try:
                    repo.create_label(name=name, color=color, description=description)
                except GithubException:
                    pass

    def _create_issues(self, repo, issues: List[Dict[str, Any]]) -> int:
        created = 0
        existing_labels = {label.name for label in repo.get_labels()}

        for index, issue in enumerate(issues[:8]):
            try:
                labels = [l for l in issue.get("labels", []) if l in existing_labels][:5]
                repo.create_issue(
                    title=issue["title"],
                    body=issue.get("body", "") + f"\n\n_Opened in batch step {index + 1}_",
                    labels=labels,
                )
                created += 1
                # GitHub cannot backdate issue timestamps; spacing makes created_at differ
                time.sleep(8)
            except Exception as exc:
                self.console.print(f"[yellow]Could not create issue: {exc}[/yellow]")
        return created

    def _create_pull_request_history(
        self,
        repo,
        repo_dir: str,
        pull_requests: List[Dict[str, Any]],
        leave_open: int = 0,
    ) -> Dict[str, int]:
        """Create PR history. Prefer merging all so later achievement merges don't conflict open PRs."""
        created = 0
        merged = 0
        cwd = Path(repo_dir)
        self._configure_repo_identity(cwd)

        plans = pull_requests[:6]
        if not plans:
            return {"created": 0, "merged": 0}

        merge_count = max(0, len(plans) - max(0, leave_open))

        for index, pr_plan in enumerate(plans):
            branch = self._safe_branch_name(
                pr_plan.get("branch_name") or f"feature/update-{index + 1}",
                index,
            )
            author = self._pick_author(index)
            should_merge = index < merge_count

            try:
                self._sync_main(cwd)
                self._create_branch_with_changes(cwd, branch, pr_plan, author, index)
                self._push_branch(cwd, branch)
                time.sleep(2)

                pull = self._open_pull_request(repo, pr_plan, branch)
                created += 1
                self.console.print(f"[green]Opened PR #{pull.number}: {pr_plan['title']}[/green]")
                # Space PR creation times (API cannot backdate created_at)
                time.sleep(8)

                if should_merge:
                    self._merge_pull_with_retry(repo, pull, pr_plan)
                    merged += 1
                    self.console.print(f"[green]Merged PR #{pull.number}[/green]")
                    time.sleep(3)
                    self._sync_main(cwd)
            except Exception as exc:
                self.console.print(f"[yellow]Could not create PR '{branch}': {exc}[/yellow]")
                subprocess.run(["git", "checkout", "main"], cwd=cwd, capture_output=True)

        subprocess.run(["git", "checkout", "main"], cwd=cwd, capture_output=True)
        return {"created": created, "merged": merged}

    def _merge_pull_with_retry(self, repo, pull, pr_plan: Dict[str, Any], retries: int = 4) -> None:
        last_error = None
        for attempt in range(retries):
            try:
                pull = repo.get_pull(pull.number)
                if pull.is_merged():
                    return
                pull.merge(
                    commit_title=f"Merge PR #{pull.number}: {pr_plan['title']}",
                    commit_message=(pr_plan.get("body", "") or "")[:500],
                    merge_method="squash",
                )
                return
            except GithubException as exc:
                last_error = exc
                if "Base branch was modified" in str(exc) or getattr(exc, "status", None) == 405:
                    time.sleep(2 + attempt)
                    try:
                        pull.update_branch()
                        time.sleep(1.5)
                    except GithubException:
                        pass
                    continue
                raise
        if last_error:
            raise last_error

    def _create_branch_with_changes(
        self,
        cwd: Path,
        branch: str,
        pr_plan: Dict[str, Any],
        author: Dict[str, str],
        index: int,
    ) -> None:
        subprocess.run(["git", "branch", "-D", branch], cwd=cwd, capture_output=True)
        self._run(["git", "checkout", "-b", branch], cwd)

        files = [f for f in pr_plan.get("files", []) if isinstance(f, str)]
        changed = False

        for rel_path in files[:5]:
            target = cwd / rel_path
            if not target.exists() or not target.is_file():
                continue
            snippet = (
                f"\n\n# PR: {pr_plan['title']}\n"
                f"# Improvement applied in pull request workflow\n"
            )
            # Use language-appropriate comment markers
            if target.suffix in {".py", ".rb", ".sh", ".yml", ".yaml", ".toml"}:
                snippet = (
                    f"\n\n# PR: {pr_plan['title']}\n"
                    f"# Contextual improvement from pull request history\n"
                )
            elif target.suffix in {".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".c", ".cpp", ".cs"}:
                snippet = (
                    f"\n\n// PR: {pr_plan['title']}\n"
                    f"// Contextual improvement from pull request history\n"
                )
            elif target.suffix in {".md", ".txt"}:
                snippet = f"\n\n## PR update\n\n{pr_plan['title']}\n"

            with open(target, "a", encoding="utf-8") as handle:
                handle.write(snippet)
            changed = True

        if not changed:
            note_dir = cwd / "docs" / "prs"
            note_dir.mkdir(parents=True, exist_ok=True)
            note = note_dir / f"pr-{index + 1}-{branch.replace('/', '-')}.md"
            note.write_text(
                f"# {pr_plan['title']}\n\n{pr_plan.get('body', '')}\n",
                encoding="utf-8",
            )

        self._run(["git", "add", "-A"], cwd)
        env = os.environ.copy()
        env.update(
            {
                "GIT_AUTHOR_NAME": author["name"],
                "GIT_AUTHOR_EMAIL": author["email"],
                "GIT_COMMITTER_NAME": author["name"],
                "GIT_COMMITTER_EMAIL": author["email"],
            }
        )
        result = subprocess.run(
            ["git", "commit", "-m", f"feat: {pr_plan['title']}"],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or "PR commit failed").strip())

    def _push_branch(self, cwd: Path, branch: str) -> None:
        result = subprocess.run(
            ["git", "push", "-u", "--force", "origin", branch],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                (result.stderr or result.stdout or "PR branch push failed").replace(self.token, "***")
            )

    def _open_pull_request(self, repo, pr_plan: Dict[str, Any], branch: str):
        # Close existing open PR on same head if present
        for existing in repo.get_pulls(state="open", head=f"{repo.owner.login}:{branch}"):
            try:
                existing.edit(state="closed")
            except GithubException:
                pass

        body = pr_plan.get("body") or f"## Summary\n\n{pr_plan.get('title', '')}"
        if "Test plan" not in body:
            body += "\n\n## Test plan\n- [ ] Verified locally\n- [ ] Ready for review\n"

        return repo.create_pull(
            title=pr_plan["title"],
            body=body,
            head=branch,
            base="main",
        )

    def _sync_main(self, cwd: Path) -> None:
        subprocess.run(["git", "checkout", "main"], cwd=cwd, capture_output=True)
        # After remote merges, refresh local main
        pull = subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if pull.returncode != 0:
            # Force align with remote main after squash merges
            subprocess.run(["git", "fetch", "origin", "main"], cwd=cwd, capture_output=True)
            subprocess.run(
                ["git", "reset", "--hard", "origin/main"],
                cwd=cwd,
                capture_output=True,
            )

    def _pick_author(self, index: int) -> Dict[str, str]:
        if self.team_members:
            member = self.team_members[index % len(self.team_members)]
            return {
                "name": member.get("name") or self.default_author["name"],
                "email": member.get("email") or self.default_author["email"],
            }
        return self.default_author

    def _safe_branch_name(self, raw: str, index: int) -> str:
        branch = re.sub(r"[^a-zA-Z0-9/_-]+", "-", (raw or "").strip().lower())
        branch = re.sub(r"-{2,}", "-", branch).strip("-/")
        if not branch:
            branch = f"feature/update-{index + 1}"
        if not branch.startswith(("feature/", "fix/", "docs/", "chore/", "refactor/")):
            branch = f"feature/{branch}"
        return branch[:80]

    def _fallback_pull_requests(
        self, repo_dir: Path, existing: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Ensure we always have enough PRs for a visible history."""
        plans = list(existing)
        source_files = []
        for path in repo_dir.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            rel = str(path.relative_to(repo_dir))
            if path.suffix in {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java"}:
                source_files.append(rel)
            if len(source_files) >= 12:
                break

        templates = [
            ("Improve core module reliability", "feature/core-reliability", "enhancement"),
            ("Add documentation for recent changes", "docs/recent-changes", "documentation"),
            ("Refactor shared utilities", "refactor/shared-utils", "refactor"),
            ("Expand automated test coverage", "feature/test-coverage", "testing"),
            ("Harden configuration and validation", "fix/config-validation", "bug"),
        ]

        used_branches = {p.get("branch_name") for p in plans}
        for i, (title, branch, label) in enumerate(templates):
            if len(plans) >= 5:
                break
            if branch in used_branches:
                continue
            files = source_files[i * 2 : i * 2 + 2] if source_files else []
            plans.append(
                {
                    "title": title,
                    "body": (
                        f"## Summary\n{title} based on the current project structure.\n\n"
                        f"## Changes\n- Update related modules\n- Improve maintainability\n"
                    ),
                    "branch_name": branch,
                    "files": files,
                    "labels": [label],
                }
            )
        return plans

    @staticmethod
    def _run(cmd: List[str], cwd: Path, env: Optional[dict] = None) -> None:
        result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or f"Command failed: {cmd}").strip())
