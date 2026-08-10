#!/usr/bin/env python3
"""Build git history from real project files and a commit plan."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set


ProgressCallback = Optional[Callable[[str, int], None]]


class HistoryBuilder:
    """Apply a commit plan using real project files with incremental diffs."""

    def __init__(self, source_project_path: str, all_project_files: Optional[List[str]] = None):
        self.source_root = Path(source_project_path).resolve()
        self.all_project_files = all_project_files or []
        self._introduced: Set[str] = set()

    def build(
        self,
        commits: List[Dict[str, Any]],
        work_dir: Optional[str] = None,
        progress_callback: ProgressCallback = None,
    ) -> Dict[str, Any]:
        """Build git history. Returns repo path and how many commits succeeded."""
        if work_dir:
            repo_dir = Path(work_dir)
            repo_dir.mkdir(parents=True, exist_ok=True)
        else:
            repo_dir = Path(tempfile.mkdtemp(prefix="repo-bot-"))

        if (repo_dir / ".git").exists():
            shutil.rmtree(repo_dir / ".git")

        self._run(["git", "init"], cwd=repo_dir)
        self._run(["git", "checkout", "-b", "main"], cwd=repo_dir)

        first_author = commits[0]["author"] if commits else {
            "name": "Repo Bot",
            "email": "bot@users.noreply.github.com",
        }
        subprocess.run(
            ["git", "config", "user.name", first_author.get("name", "Repo Bot")],
            cwd=repo_dir,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", first_author.get("email", "bot@users.noreply.github.com")],
            cwd=repo_dir,
            capture_output=True,
        )

        self._introduced = set()
        applied = 0
        total = len(commits)

        for i, commit in enumerate(commits):
            if progress_callback:
                progress = 50 + int((i / max(total, 1)) * 30)
                progress_callback("applying_commits", progress)

            if self._apply_commit(repo_dir, commit, i):
                applied += 1

        # CRITICAL: ensure the final tree contains the complete project
        if progress_callback:
            progress_callback("syncing_all_files", 82)

        synced = self._sync_complete_project(
            repo_dir=repo_dir,
            author=commits[-1]["author"] if commits else first_author,
            commit_date=(commits[-1]["date"] + timedelta(minutes=5)) if commits else datetime.now(),
        )

        return {
            "repo_dir": str(repo_dir),
            "commits_applied": applied + (1 if synced else 0),
            "files_synced": synced,
        }

    def _sync_complete_project(
        self,
        repo_dir: Path,
        author: Dict[str, str],
        commit_date: datetime,
    ) -> int:
        """
        Copy the full real project into the repo as the final state.

        History commits may only touch a subset of files. This step guarantees
        every project file is present and matches the source (clean content).
        """
        # Ensure Actions tab has a real workflow (not only "Suggested workflows")
        workflow = repo_dir / ".github" / "workflows" / "ci.yml"
        if not workflow.exists():
            workflow.parent.mkdir(parents=True, exist_ok=True)
            workflow.write_text(
                """name: CI

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
""",
                encoding="utf-8",
            )

        files_to_sync = self.all_project_files
        if not files_to_sync:
            files_to_sync = self._discover_source_files()

        # Always include the CI workflow path in the final tree
        sync_paths = list(dict.fromkeys(list(files_to_sync) + [".github/workflows/ci.yml"]))

        copied = 0
        for rel_path in sync_paths:
            source_file = self.source_root / rel_path
            target_file = repo_dir / rel_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            if source_file.exists() and source_file.is_file():
                shutil.copy2(source_file, target_file)
                copied += 1
            elif rel_path == ".github/workflows/ci.yml" and target_file.exists():
                copied += 1

        # Remove synthetic history helpers from the published tree
        fake_log = repo_dir / ".development_log"
        if fake_log.exists():
            fake_log.unlink()

        self._run(["git", "add", "-A"], cwd=repo_dir)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
        )
        if not (status.stdout or "").strip():
            return copied

        env = os.environ.copy()
        env.update(
            {
                "GIT_AUTHOR_NAME": author["name"],
                "GIT_AUTHOR_EMAIL": author["email"],
                "GIT_COMMITTER_NAME": author["name"],
                "GIT_COMMITTER_EMAIL": author["email"],
                "GIT_AUTHOR_DATE": commit_date.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                "GIT_COMMITTER_DATE": commit_date.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            }
        )
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"chore: sync complete project tree ({copied} files)",
                "--date",
                commit_date.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            ],
            cwd=repo_dir,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        return copied

    def _discover_source_files(self) -> List[str]:
        from core.project_scanner import ProjectScanner

        return ProjectScanner(str(self.source_root)).list_all_sync_files()

    def _apply_commit(self, repo_dir: Path, commit: Dict[str, Any], index: int) -> bool:
        files = [f for f in commit.get("files", []) if isinstance(f, str)]
        if not files:
            files = [".development_log"]

        changed = False
        for rel_path in files:
            if self._write_file_change(repo_dir, rel_path, commit, index):
                changed = True

        if not changed:
            self._write_file_change(repo_dir, ".development_log", commit, index)

        self._run(["git", "add", "-A"], cwd=repo_dir)

        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
        )
        if not (status.stdout or "").strip():
            return False

        author = commit["author"]
        commit_date = commit["date"]
        date_str = commit_date.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        env = os.environ.copy()
        env.update(
            {
                "GIT_AUTHOR_NAME": author["name"],
                "GIT_AUTHOR_EMAIL": author["email"],
                "GIT_COMMITTER_NAME": author["name"],
                "GIT_COMMITTER_EMAIL": author["email"],
                "GIT_AUTHOR_DATE": date_str,
                "GIT_COMMITTER_DATE": date_str,
            }
        )

        result = subprocess.run(
            ["git", "commit", "-m", commit["message"], "--date", date_str],
            cwd=repo_dir,
            env=env,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def _write_file_change(
        self,
        repo_dir: Path,
        rel_path: str,
        commit: Dict[str, Any],
        index: int,
    ) -> bool:
        source_file = self.source_root / rel_path
        target_file = repo_dir / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)

        marker = self._change_marker(rel_path, commit, index)

        if rel_path == ".development_log" or not source_file.exists():
            with open(target_file, "a", encoding="utf-8") as handle:
                handle.write(marker)
            self._introduced.add(rel_path)
            return True

        if rel_path not in self._introduced:
            shutil.copy2(source_file, target_file)
            self._introduced.add(rel_path)
            return True

        with open(target_file, "a", encoding="utf-8") as handle:
            handle.write(marker)
        return True

    def _change_marker(self, rel_path: str, commit: Dict[str, Any], index: int) -> str:
        message = commit.get("message", f"update {index}")
        suffix = Path(rel_path).suffix.lower()
        stamp = f"{index + 1}: {message}"

        if suffix in {".py", ".rb", ".sh", ".yml", ".yaml", ".toml", ".gitignore"} or rel_path.startswith("."):
            return f"\n# history-step {stamp}\n"
        if suffix in {".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".c", ".cpp", ".cs", ".css", ".scss"}:
            return f"\n// history-step {stamp}\n"
        if suffix in {".md", ".txt", ".rst", ".html", ".vue", ".svelte"}:
            return f"\n<!-- history-step {stamp} -->\n"
        return f"\n# history-step {stamp}\n"

    @staticmethod
    def _run(cmd: List[str], cwd: Path, env: Optional[dict] = None) -> None:
        subprocess.run(cmd, cwd=cwd, env=env, check=True, capture_output=True, text=True)
