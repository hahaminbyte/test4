#!/usr/bin/env python3
"""Plan realistic commit history from actual project files."""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from core.ai_client import AIClient
from core.project_scanner import ProjectSnapshot


COMMIT_PLAN_SYSTEM_PROMPT = """You are planning a realistic git commit history for an EXISTING project.
Return valid JSON only.

The commits must reflect how this specific project would have been built incrementally.
Use REAL file paths from the project. Do NOT invent files that don't exist.

Output schema:
{
  "commits": [
    {
      "message": "commit message matching the requested style",
      "type": "feat|fix|refactor|docs|test|chore|perf",
      "author_index": 0,
      "day_offset": 0,
      "hour": 10,
      "files": ["path/to/file1", "path/to/file2"],
      "description": "what this commit actually does in the project"
    }
  ]
}

Rules:
- return EXACTLY the requested number of commits
- every file path MUST exist in the provided inventory
- files MAY appear in multiple commits (later commits refine earlier work)
- commit messages must mention real modules/features from the project
- author_index refers to the team member index provided
- day_offset is days from project start (0 = earliest)
- spread commits across the requested timeline naturally
"""


class CommitPlanner:
    """Generate a commit plan grounded in real project files."""

    COMMIT_TYPE_WEIGHTS = {
        "feat": 0.35,
        "fix": 0.2,
        "refactor": 0.15,
        "test": 0.1,
        "docs": 0.1,
        "chore": 0.07,
        "perf": 0.03,
    }

    def __init__(self, ai_client: AIClient):
        self.ai = ai_client

    def plan(
        self,
        snapshot: ProjectSnapshot,
        analysis: Dict[str, Any],
        num_commits: int,
        days_back: int,
        team_members: List[Dict[str, Any]],
        commit_style: str = "conventional",
    ) -> List[Dict[str, Any]]:
        num_commits = max(5, int(num_commits))
        commit_style = (commit_style or "conventional").lower()

        commits: List[Dict[str, Any]] = []
        if self.ai.available:
            try:
                commits = self._plan_with_ai(
                    snapshot, analysis, num_commits, days_back, team_members, commit_style
                )
            except Exception:
                commits = []

        if len(commits) < num_commits:
            local = self._plan_locally(
                snapshot, analysis, num_commits, days_back, team_members, commit_style
            )
            # Keep AI commits first, then pad with local ones
            commits = commits + local[len(commits) :]

        commits = commits[:num_commits]
        if len(commits) < num_commits:
            commits = self._pad_commits(
                commits, snapshot, analysis, num_commits, days_back, team_members, commit_style
            )

        return self._finalize_commits(
            commits, snapshot, team_members, days_back, commit_style
        )

    def _plan_with_ai(
        self,
        snapshot: ProjectSnapshot,
        analysis: Dict[str, Any],
        num_commits: int,
        days_back: int,
        team_members: List[Dict[str, Any]],
        commit_style: str,
    ) -> List[Dict[str, Any]]:
        file_inventory = [
            {"path": f.path, "category": f.category, "preview": f.preview[:300]}
            for f in snapshot.files
        ]
        team_info = [
            {"index": i, "name": m["name"], "role": m.get("role", "Developer")}
            for i, m in enumerate(team_members)
        ]

        style_rules = {
            "conventional": "Use Conventional Commits strictly: type(scope): description",
            "descriptive": "Use full-sentence descriptive messages without type prefixes",
            "mixed": "Mix conventional prefixes and descriptive sentences across commits",
        }

        user_prompt = f"""Plan EXACTLY {num_commits} commits over {days_back} days for this project.

Project summary: {analysis.get('summary', '')}
Architecture: {analysis.get('architecture', '')}
Tech stack: {', '.join(analysis.get('tech_stack', []))}
Commit style: {commit_style}
Style rule: {style_rules.get(commit_style, style_rules['conventional'])}

Team members:
{team_info}

All files (use ONLY these paths; files can be reused across commits):
{file_inventory}

Development phases:
{analysis.get('development_phases', [])}

IMPORTANT: Return exactly {num_commits} commits in the JSON array.
Order commits logically: setup -> core features -> tests -> docs/polish.
"""

        result = self.ai.chat_json(COMMIT_PLAN_SYSTEM_PROMPT, user_prompt, temperature=0.5)
        commits = result.get("commits", [])

        valid_paths = {f.path for f in snapshot.files}
        validated = []
        for commit in commits:
            files = [f for f in commit.get("files", []) if f in valid_paths]
            if not files and valid_paths:
                files = [random.choice(list(valid_paths))]
            if not files:
                continue
            commit["files"] = files
            validated.append(commit)

        return validated

    def _plan_locally(
        self,
        snapshot: ProjectSnapshot,
        analysis: Dict[str, Any],
        num_commits: int,
        days_back: int,
        team_members: List[Dict[str, Any]],
        commit_style: str = "conventional",
    ) -> List[Dict[str, Any]]:
        ordered_files = self._ordered_files(snapshot)
        if not ordered_files:
            ordered_files = [".development_log"]

        commits = []
        day_step = max(0.5, days_back / num_commits)

        for i in range(num_commits):
            # Cycle through files so we can create more commits than file count
            if i < len(ordered_files):
                batch = [ordered_files[i]]
                # Early commits may introduce a small group
                if i < max(3, len(ordered_files) // 10):
                    end = min(i + 2, len(ordered_files))
                    batch = ordered_files[i:end] or batch
            else:
                # Later commits refine already-introduced files
                primary = ordered_files[i % len(ordered_files)]
                secondary = ordered_files[(i * 3) % len(ordered_files)]
                batch = list(dict.fromkeys([primary, secondary]))

            commit_type = self._weighted_commit_type(i, num_commits)
            primary_file = batch[0]
            module = self._module_name(primary_file)
            message = self._format_message(
                commit_style,
                commit_type,
                primary_file,
                module,
                analysis,
                batch,
            )

            commits.append(
                {
                    "message": message,
                    "type": commit_type,
                    "author_index": self._pick_author_index(i, team_members),
                    "day_offset": min(int(i * day_step), days_back),
                    "hour": random.randint(9, 18),
                    "files": batch,
                    "description": f"Add/update {', '.join(batch[:3])}",
                }
            )

        return commits

    def _pad_commits(
        self,
        commits: List[Dict[str, Any]],
        snapshot: ProjectSnapshot,
        analysis: Dict[str, Any],
        num_commits: int,
        days_back: int,
        team_members: List[Dict[str, Any]],
        commit_style: str,
    ) -> List[Dict[str, Any]]:
        ordered_files = self._ordered_files(snapshot) or [".development_log"]
        padded = list(commits)
        i = len(padded)
        while len(padded) < num_commits:
            primary = ordered_files[i % len(ordered_files)]
            commit_type = self._weighted_commit_type(i, num_commits)
            module = self._module_name(primary)
            padded.append(
                {
                    "message": self._format_message(
                        commit_style, commit_type, primary, module, analysis, [primary]
                    ),
                    "type": commit_type,
                    "author_index": self._pick_author_index(i, team_members),
                    "day_offset": min(int(i * (days_back / num_commits)), days_back),
                    "hour": random.randint(9, 18),
                    "files": [primary],
                    "description": f"Iterate on {primary}",
                }
            )
            i += 1
        return padded

    def _finalize_commits(
        self,
        commits: List[Dict[str, Any]],
        snapshot: ProjectSnapshot,
        team_members: List[Dict[str, Any]],
        days_back: int,
        commit_style: str = "conventional",
    ) -> List[Dict[str, Any]]:
        start_date = datetime.now() - timedelta(days=days_back)
        valid = {f.path for f in snapshot.files}
        ordered_files = self._ordered_files(snapshot) or [".development_log"]
        finalized = []

        for i, commit in enumerate(commits):
            author_index = commit.get("author_index", i % max(len(team_members), 1))
            author_index = max(0, min(author_index, len(team_members) - 1))
            author = team_members[author_index]

            day_offset = commit.get("day_offset", int(i * (days_back / max(len(commits), 1))))
            hour = commit.get("hour", random.randint(9, 18))
            commit_date = start_date + timedelta(
                days=int(day_offset),
                hours=hour % 24,
                minutes=random.randint(0, 59),
            )

            files = [f for f in commit.get("files", []) if f in valid]
            if not files:
                files = [ordered_files[i % len(ordered_files)]]

            message = commit.get("message") or self._format_message(
                commit_style,
                commit.get("type", "chore"),
                files[0],
                self._module_name(files[0]),
                {},
                files,
            )
            message = self._apply_style(message, commit_style, commit.get("type", "chore"))

            finalized.append(
                {
                    "message": message,
                    "type": commit.get("type", "chore"),
                    "author": author,
                    "date": commit_date,
                    "files": files,
                    "description": commit.get("description", ""),
                }
            )

        finalized.sort(key=lambda c: c["date"])
        return finalized

    def _ordered_files(self, snapshot: ProjectSnapshot) -> List[str]:
        files_by_category: Dict[str, List[str]] = {}
        for project_file in snapshot.files:
            if project_file.category == "other" and project_file.size > 20_000:
                continue
            files_by_category.setdefault(project_file.category, []).append(project_file.path)

        ordered: List[str] = []
        for category in ["meta", "config", "source", "frontend", "tests", "docs", "other"]:
            ordered.extend(files_by_category.get(category, []))
        return ordered or [f.path for f in snapshot.files]

    def _weighted_commit_type(self, index: int, total: int) -> str:
        progress = index / max(total - 1, 1)
        if progress < 0.15:
            return random.choices(["feat", "chore"], weights=[0.4, 0.6])[0]
        if progress > 0.85:
            return random.choices(["docs", "test", "fix", "refactor"], weights=[0.4, 0.3, 0.2, 0.1])[0]
        types = list(self.COMMIT_TYPE_WEIGHTS.keys())
        weights = list(self.COMMIT_TYPE_WEIGHTS.values())
        return random.choices(types, weights=weights)[0]

    def _module_name(self, path: str) -> str:
        parts = path.replace("\\", "/").split("/")
        if len(parts) >= 2:
            return parts[-2]
        return Path(path).stem

    def _format_message(
        self,
        commit_style: str,
        commit_type: str,
        primary_file: str,
        module: str,
        analysis: Dict[str, Any],
        batch: List[str],
    ) -> str:
        feature_names = [f["name"] for f in analysis.get("features", [])]
        feature = feature_names[0] if feature_names else module

        conventional = {
            "feat": [
                f"feat({module}): implement {feature} in `{primary_file}`",
                f"feat: add {module} module with core logic",
            ],
            "fix": [
                f"fix({module}): handle edge cases in `{primary_file}`",
                f"fix: resolve validation issue in {module}",
            ],
            "refactor": [
                f"refactor({module}): restructure `{primary_file}`",
                f"refactor: improve organization of {module} files",
            ],
            "test": [
                f"test({module}): add tests for `{primary_file}`",
                f"test: expand coverage for {module}",
            ],
            "docs": [
                f"docs: update documentation for {module}",
                f"docs: add usage notes for `{primary_file}`",
            ],
            "chore": [
                f"chore: update project configuration",
                f"chore({module}): update build and tooling setup",
            ],
            "perf": [f"perf({module}): optimize `{primary_file}`"],
        }
        descriptive = {
            "feat": [
                f"Implement {feature} support inside {module}",
                f"Add core logic for {module} using `{primary_file}`",
            ],
            "fix": [
                f"Resolve edge-case failures in `{primary_file}`",
                f"Correct validation behavior in the {module} module",
            ],
            "refactor": [
                f"Restructure `{primary_file}` for clearer maintainability",
                f"Clean up shared logic within {module}",
            ],
            "test": [
                f"Add automated coverage around `{primary_file}`",
                f"Strengthen regression tests for {module}",
            ],
            "docs": [
                f"Document usage and setup details for {module}",
                f"Clarify contribution notes related to `{primary_file}`",
            ],
            "chore": [
                f"Refresh tooling and configuration for ongoing development",
                f"Adjust project setup around {module}",
            ],
            "perf": [f"Improve runtime efficiency in `{primary_file}`"],
        }

        pool = conventional if commit_style == "conventional" else descriptive
        if commit_style == "mixed":
            pool = conventional if random.random() < 0.5 else descriptive

        message = random.choice(pool.get(commit_type, [f"Update `{primary_file}`"]))
        if len(batch) > 1:
            message += f" (+{len(batch) - 1} files)"
        return message

    def _apply_style(self, message: str, commit_style: str, commit_type: str) -> str:
        message = (message or "").strip()
        if not message:
            return f"{commit_type}: update project files"

        has_prefix = ":" in message.split(" ")[0] or message.startswith(
            ("feat", "fix", "docs", "test", "chore", "refactor", "perf", "style", "ci", "build")
        )

        if commit_style == "conventional" and not has_prefix:
            return f"{commit_type}: {message[0].lower() + message[1:]}"
        if commit_style == "descriptive" and has_prefix and ":" in message:
            # Strip conventional prefix
            remainder = message.split(":", 1)[1].strip()
            return remainder[0].upper() + remainder[1:] if remainder else message
        return message

    def _pick_author_index(self, commit_index: int, team_members: List[Dict[str, Any]]) -> int:
        weights = {"high": 3, "medium": 2, "low": 1}
        author_weights = [weights.get(m.get("activity_level", "medium"), 1) for m in team_members]
        return random.choices(range(len(team_members)), weights=author_weights)[0]
