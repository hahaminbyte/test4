#!/usr/bin/env python3
"""
GitHub profile achievement unlocker.

Automates several publicly documented profile badges on a repository you own:
- Pull Shark          : merged pull requests
- Pair Extraordinaire : commits with Co-authored-by trailers
- YOLO                : merge PRs without review
- Quickdraw           : open and close an issue within 5 minutes
- Heart On Your Sleeve: add emoji reactions on issues/PRs
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

from github import Github
from github.GithubException import GithubException
from rich.console import Console

ProgressCallback = Optional[Callable[[str, int], None]]

PULL_SHARK_TIERS = {
    "default": 2,
    "bronze": 16,
    "silver": 128,
    "gold": 1024,
}

PAIR_TIERS = {
    "default": 1,
    "bronze": 10,
    "silver": 24,
    "gold": 48,
}

SUPPORTED_BADGES = [
    "pull_shark",
    "pair_extraordinaire",
    "yolo",
    "quickdraw",
    "heart_on_your_sleeve",
]


class AchievementUnlocker:
    """Unlock multiple GitHub profile achievements on a target repository."""

    def __init__(
        self,
        github_token: str,
        team_members: Optional[List[Dict[str, Any]]] = None,
    ):
        self.token = github_token.strip()
        self.github = Github(self.token)
        self.user = self.github.get_user()
        self.login = self.user.login
        self.console = Console()
        self.team_members = team_members or []

    def unlock(
        self,
        repo_name: str,
        badges: Optional[List[str]] = None,
        pull_shark_count: int = 16,
        pair_count: int = 10,
        reaction_rounds: int = 20,
        delay_seconds: float = 3.0,
        progress_callback: ProgressCallback = None,
    ) -> Dict[str, Any]:
        badges = [b for b in (badges or SUPPORTED_BADGES) if b in SUPPORTED_BADGES]
        if not badges:
            return {"success": False, "error": "No supported badges selected", "results": {}}

        repo = self.user.get_repo(repo_name)
        results: Dict[str, Any] = {}
        total = len(badges)

        for index, badge in enumerate(badges):
            if progress_callback:
                progress_callback(f"unlocking_{badge}", 90 + int((index / max(total, 1)) * 8))

            self.console.print(f"[blue]Unlocking badge:[/blue] {badge}")
            try:
                if badge == "pull_shark":
                    results[badge] = self._unlock_pull_shark(repo, pull_shark_count, delay_seconds)
                elif badge == "pair_extraordinaire":
                    results[badge] = self._unlock_pair_extraordinaire(repo, pair_count, delay_seconds)
                elif badge == "yolo":
                    results[badge] = self._unlock_yolo(repo, delay_seconds)
                elif badge == "quickdraw":
                    results[badge] = self._unlock_quickdraw(repo)
                elif badge == "heart_on_your_sleeve":
                    results[badge] = self._unlock_heart(repo, reaction_rounds, delay_seconds)
            except Exception as exc:
                results[badge] = {"success": False, "error": str(exc)}
                self.console.print(f"[yellow]Badge {badge} failed: {exc}[/yellow]")

        earned = [name for name, data in results.items() if data.get("success")]
        return {
            "success": bool(earned),
            "repository": repo.html_url,
            "requested": badges,
            "earned": earned,
            "results": results,
        }

    def _coauthors(self) -> List[Dict[str, str]]:
        authors = []
        for member in self.team_members:
            name = member.get("name")
            email = member.get("email")
            if name and email:
                authors.append({"name": name, "email": email})
        if len(authors) < 2:
            authors.extend(
                [
                    {"name": "Alex Rivera", "email": "alex.rivera@users.noreply.github.com"},
                    {"name": "Sarah Chen", "email": "sarah.chen@users.noreply.github.com"},
                ]
            )
        return authors[:4]

    def _ensure_readme(self, repo) -> None:
        try:
            repo.get_contents("README.md")
        except GithubException:
            repo.create_file(
                "README.md",
                "chore: add readme for achievement automation",
                f"# {repo.name}\n\nAutomated achievement workspace.\n",
                branch=repo.default_branch,
            )

    def _create_branch_from_default(self, repo, branch_name: str) -> str:
        base = repo.default_branch
        # Always branch from the latest default SHA
        source = repo.get_branch(base)
        try:
            ref = repo.get_git_ref(f"heads/{branch_name}")
            ref.delete()
            time.sleep(0.5)
        except GithubException:
            pass
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)
        return base

    def _update_file_on_branch(self, repo, path: str, branch: str, message: str, suffix: str) -> None:
        try:
            content = repo.get_contents(path, ref=branch)
            body = content.decoded_content.decode("utf-8", errors="replace")
            repo.update_file(path, message, body + suffix, content.sha, branch=branch)
        except GithubException:
            repo.create_file(path, message, suffix.lstrip("\n"), branch=branch)

    def _merge_with_retry(self, repo, pr, commit_title: str, commit_message: str = "", merge_method: str = "squash", retries: int = 4):
        """Merge PR, recovering from 'Base branch was modified' races."""
        last_error = None
        for attempt in range(retries):
            try:
                # Refresh PR object
                pr = repo.get_pull(pr.number)
                if pr.is_merged():
                    return pr
                kwargs = {"commit_title": commit_title, "merge_method": merge_method}
                if commit_message:
                    kwargs["commit_message"] = commit_message
                pr.merge(**kwargs)
                return pr
            except GithubException as exc:
                last_error = exc
                message = str(exc)
                if "Base branch was modified" in message or getattr(exc, "status", None) == 405:
                    self.console.print(
                        f"[yellow]Merge race on PR #{pr.number}, retry {attempt + 1}/{retries}...[/yellow]"
                    )
                    time.sleep(2 + attempt)
                    try:
                        # Update PR branch onto latest base, then retry
                        pr.update_branch()
                        time.sleep(1.5)
                    except GithubException:
                        # Recreate from latest main if update_branch is unavailable
                        break
                    continue
                raise
        # Last resort: close stale PR and recreate from latest main tip
        raise last_error or RuntimeError(f"Failed to merge PR #{pr.number}")

    def _create_and_merge_pr(
        self,
        repo,
        branch: str,
        file_path: str,
        commit_message: str,
        pr_title: str,
        pr_body: str,
        suffix: str,
        merge_method: str = "squash",
        merge_title: Optional[str] = None,
        merge_message: str = "",
        delay: float = 3.0,
    ):
        base = self._create_branch_from_default(repo, branch)
        self._update_file_on_branch(repo, file_path, branch, commit_message, suffix)
        time.sleep(1.0)
        pr = repo.create_pull(title=pr_title, body=pr_body, head=branch, base=base)
        time.sleep(1.5)
        self._merge_with_retry(
            repo,
            pr,
            commit_title=merge_title or pr_title,
            commit_message=merge_message or commit_message,
            merge_method=merge_method,
        )
        time.sleep(delay)
        return pr

    def _unlock_pull_shark(self, repo, count: int, delay: float) -> Dict[str, Any]:
        self._ensure_readme(repo)
        count = max(1, min(int(count), 128))
        merged = 0
        pr_numbers = []
        errors = []

        for i in range(1, count + 1):
            branch = f"achievement/pull-shark-{int(time.time())}-{i}"
            try:
                pr = self._create_and_merge_pr(
                    repo=repo,
                    branch=branch,
                    file_path="ACHIEVEMENTS.md",
                    commit_message=f"chore: pull shark batch {i}",
                    pr_title=f"chore: Pull Shark batch #{i}",
                    pr_body="Automated merged PR for Pull Shark profile achievement.",
                    suffix=f"\n- Pull Shark update #{i} at {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
                    merge_title=f"chore: merge pull shark #{i}",
                    delay=delay,
                )
                merged += 1
                pr_numbers.append(pr.number)
                self.console.print(f"[green]Merged PR #{pr.number} ({merged}/{count})[/green]")
            except Exception as exc:
                errors.append(str(exc))
                self.console.print(f"[yellow]Pull Shark item {i} failed: {exc}[/yellow]")
                time.sleep(delay)

        return {
            "success": merged >= 2,
            "merged": merged,
            "target": count,
            "pr_numbers": pr_numbers,
            "errors": errors[:5],
            "badge": "Pull Shark",
            "note": "Tiers unlock at 2 / 16 / 128 / 1024 merged PRs. May take hours to appear.",
        }

    def _unlock_pair_extraordinaire(self, repo, count: int, delay: float) -> Dict[str, Any]:
        self._ensure_readme(repo)
        count = max(1, min(int(count), 48))
        coauthors = self._coauthors()
        created = 0
        pr_numbers = []
        errors = []

        for i in range(1, count + 1):
            branch = f"achievement/pair-{int(time.time())}-{i}"
            trailers = "\n".join(
                f"Co-authored-by: {a['name']} <{a['email']}>" for a in coauthors[:2]
            )
            commit_message = (
                f"chore: pair programming session {i}\n\n"
                f"Collaborative update for Pair Extraordinaire.\n\n"
                f"{trailers}"
            )
            try:
                pr = self._create_and_merge_pr(
                    repo=repo,
                    branch=branch,
                    file_path="PAIRING.md",
                    commit_message=commit_message,
                    pr_title=f"chore: Pair Extraordinaire session #{i}",
                    pr_body=f"Coauthored collaboration batch #{i}.\n\n{trailers}",
                    suffix=f"\n- Pairing session #{i} at {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
                    merge_title=commit_message.split("\n", 1)[0],
                    merge_message=commit_message,
                    delay=delay,
                )
                created += 1
                pr_numbers.append(pr.number)
                self.console.print(f"[green]Coauthored merge #{created}/{count}[/green]")
            except Exception as exc:
                errors.append(str(exc))
                self.console.print(f"[yellow]Pair item {i} failed: {exc}[/yellow]")
                time.sleep(delay)

        return {
            "success": created >= 1,
            "coauthored_merges": created,
            "target": count,
            "pr_numbers": pr_numbers,
            "errors": errors[:5],
            "badge": "Pair Extraordinaire",
            "note": "Tiers unlock at 1 / 10 / 24 / 48 coauthored commits.",
        }

    def _unlock_yolo(self, repo, delay: float) -> Dict[str, Any]:
        self._ensure_readme(repo)
        branch = f"achievement/yolo-{int(time.time())}"
        pr = self._create_and_merge_pr(
            repo=repo,
            branch=branch,
            file_path="YOLO.md",
            commit_message="chore: yolo merge without review",
            pr_title="chore: YOLO achievement merge",
            pr_body="Merged without requesting or waiting for review.",
            suffix="\nYOLO merge — no reviewers required.\n",
            merge_method="merge",
            merge_title="chore: YOLO merge",
            delay=delay,
        )
        return {
            "success": True,
            "merged_pr": pr.number,
            "badge": "YOLO",
            "note": "Requires merging a PR without a review.",
        }

    def _unlock_quickdraw(self, repo) -> Dict[str, Any]:
        issue = repo.create_issue(
            title=f"Quickdraw achievement check {int(time.time())}",
            body="Opening and closing immediately for the Quickdraw profile badge.",
        )
        time.sleep(1)
        issue.edit(state="closed")
        return {
            "success": True,
            "issue_number": issue.number,
            "badge": "Quickdraw",
            "note": "Close an issue or PR within 5 minutes of opening it.",
        }

    def _unlock_heart(self, repo, rounds: int, delay: float) -> Dict[str, Any]:
        rounds = max(5, min(int(rounds), 100))
        reactions = ["+1", "heart", "rocket", "eyes", "laugh", "hooray"]
        added = 0

        issues = list(repo.get_issues(state="all")[:8])
        if not issues:
            for i in range(3):
                issues.append(
                    repo.create_issue(
                        title=f"Reaction target #{i + 1}",
                        body="Target issue for Heart On Your Sleeve reactions.",
                    )
                )
                time.sleep(2)

        for i in range(rounds):
            issue = issues[i % len(issues)]
            reaction = reactions[i % len(reactions)]
            try:
                issue.create_reaction(reaction)
                added += 1
            except GithubException:
                continue
            time.sleep(max(0.4, delay / 2))

        return {
            "success": added > 0,
            "reactions_added": added,
            "badge": "Heart On Your Sleeve",
            "note": "Granted for reacting to content on GitHub.",
        }


def describe_badges() -> List[Dict[str, str]]:
    return [
        {
            "id": "pull_shark",
            "name": "Pull Shark",
            "description": "Merge pull requests (tiers at 2 / 16 / 128 / 1024)",
        },
        {
            "id": "pair_extraordinaire",
            "name": "Pair Extraordinaire",
            "description": "Coauthored commits (tiers at 1 / 10 / 24 / 48)",
        },
        {
            "id": "yolo",
            "name": "YOLO",
            "description": "Merge a pull request without a review",
        },
        {
            "id": "quickdraw",
            "name": "Quickdraw",
            "description": "Close an issue/PR within 5 minutes of opening",
        },
        {
            "id": "heart_on_your_sleeve",
            "name": "Heart On Your Sleeve",
            "description": "React to issues and pull requests",
        },
    ]
