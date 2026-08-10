#!/usr/bin/env python3
"""AI-powered deep analysis of existing projects."""

from __future__ import annotations

from typing import Any, Dict, List

from core.ai_client import AIClient
from core.project_scanner import ProjectSnapshot


ANALYSIS_SYSTEM_PROMPT = """You are a senior software architect analyzing a real codebase.
Return valid JSON only.

Your job is to deeply understand the project and produce analysis that reflects the ACTUAL code,
not generic templates. Reference real file paths, modules, technologies, and patterns you see.

Output schema:
{
  "summary": "2-3 sentence overview of what this project actually does",
  "architecture": "description of architecture patterns used",
  "modules": [{"name": "...", "description": "...", "files": ["path1", "path2"]}],
  "features": [{"name": "...", "description": "...", "files": ["..."]}],
  "tech_stack": ["..."],
  "development_phases": [
    {"name": "...", "description": "...", "focus_files": ["..."], "duration_days": 7}
  ],
  "complexity": "low|medium|high",
  "issues": [
    {
      "title": "...",
      "body": "markdown body referencing actual project areas",
      "labels": ["bug|enhancement|documentation|security|performance"]
    }
  ],
  "pull_requests": [
    {
      "title": "...",
      "body": "markdown body",
      "branch_name": "feature/...",
      "files": ["files changed in this PR"],
      "labels": ["enhancement"]
    }
  ]
}

Rules:
- issues and pull_requests must reference REAL aspects of this specific project
- do NOT invent generic placeholder issues
- pull_requests should represent realistic feature branches that could exist in this repo
- generate 3-5 issues and 4-6 pull requests covering different areas
- prefer concrete module/file names from the inventory in PR titles and bodies
- set branch_name like feature/..., fix/..., docs/..., refactor/...
"""


class AIAnalyzer:
    """Perform deep AI analysis on a scanned project."""

    def __init__(self, ai_client: AIClient):
        self.ai = ai_client

    def analyze(self, snapshot: ProjectSnapshot) -> Dict[str, Any]:
        if self.ai.available:
            return self._analyze_with_ai(snapshot)
        return self._analyze_locally(snapshot)

    def _analyze_with_ai(self, snapshot: ProjectSnapshot) -> Dict[str, Any]:
        summary = snapshot.to_summary()
        user_prompt = f"""Analyze this existing project deeply.

Project: {snapshot.name}
Root: {snapshot.root}
Language: {snapshot.detected_language}
Frameworks: {', '.join(snapshot.detected_frameworks) or 'none detected'}
Dependencies: {', '.join(snapshot.dependencies[:40]) or 'none detected'}

File inventory ({snapshot.file_count} files analyzed):
{self._format_files_for_prompt(snapshot)}

Produce contextual issues and 4-6 pull requests that match this codebase.
Pull requests should cover different areas (features, fixes, docs, refactor, tests).
"""

        result = self.ai.chat_json(ANALYSIS_SYSTEM_PROMPT, user_prompt)
        result.setdefault("summary", f"Project {snapshot.name} written in {snapshot.detected_language}")
        result.setdefault("tech_stack", snapshot.detected_frameworks or [snapshot.detected_language])
        result.setdefault("issues", [])
        result.setdefault("pull_requests", [])
        result.setdefault("development_phases", self._default_phases(snapshot))
        return result

    def _analyze_locally(self, snapshot: ProjectSnapshot) -> Dict[str, Any]:
        modules = self._group_modules(snapshot)
        features = self._infer_features(snapshot)

        return {
            "summary": (
                f"{snapshot.name} is a {snapshot.detected_language} project"
                f" using {', '.join(snapshot.detected_frameworks) or 'standard tooling'}."
            ),
            "architecture": "Layered application structure inferred from directory layout.",
            "modules": modules,
            "features": features,
            "tech_stack": snapshot.detected_frameworks or [snapshot.detected_language],
            "development_phases": self._default_phases(snapshot),
            "complexity": "medium",
            "issues": self._local_issues(snapshot, features),
            "pull_requests": self._local_pull_requests(snapshot, features),
        }

    def _format_files_for_prompt(self, snapshot: ProjectSnapshot) -> str:
        lines = []
        for project_file in snapshot.files[:80]:
            lines.append(
                f"- {project_file.path} [{project_file.category}] ({project_file.size} bytes)\n"
                f"  Preview:\n{project_file.preview[:800]}"
            )
        if len(snapshot.files) > 80:
            lines.append(f"... and {len(snapshot.files) - 80} more files")
        return "\n".join(lines)

    def _default_phases(self, snapshot: ProjectSnapshot) -> List[Dict[str, Any]]:
        phases = [
            {
                "name": "Project Setup",
                "description": "Initial repository scaffolding and configuration",
                "focus_files": [f.path for f in snapshot.files if f.category in {"meta", "config"}][:8],
                "duration_days": 3,
            },
            {
                "name": "Core Implementation",
                "description": "Primary application logic and services",
                "focus_files": [f.path for f in snapshot.files if f.category == "source"][:20],
                "duration_days": 21,
            },
            {
                "name": "Testing & Quality",
                "description": "Test coverage and bug fixes",
                "focus_files": [f.path for f in snapshot.files if f.category == "tests"][:10],
                "duration_days": 10,
            },
            {
                "name": "Documentation & Polish",
                "description": "Documentation and final refinements",
                "focus_files": [f.path for f in snapshot.files if f.category == "docs"][:8],
                "duration_days": 7,
            },
        ]
        return [p for p in phases if p["focus_files"]]

    def _group_modules(self, snapshot: ProjectSnapshot) -> List[Dict[str, Any]]:
        buckets: Dict[str, List[str]] = {}
        for project_file in snapshot.files:
            if project_file.category not in {"source", "frontend"}:
                continue
            parts = project_file.path.split("/")
            module = parts[1] if len(parts) > 1 else parts[0]
            buckets.setdefault(module, []).append(project_file.path)

        return [
            {"name": name, "description": f"Module containing {len(paths)} files", "files": paths[:10]}
            for name, paths in sorted(buckets.items())
        ][:8]

    def _infer_features(self, snapshot: ProjectSnapshot) -> List[Dict[str, Any]]:
        keywords = {
            "authentication": ["auth", "login", "jwt", "session"],
            "api": ["api", "route", "controller", "endpoint"],
            "database": ["db", "model", "schema", "migration", "repository"],
            "frontend": ["component", "page", "view", "ui"],
            "testing": ["test", "spec"],
        }
        features = []
        for name, terms in keywords.items():
            matched = [
                f.path
                for f in snapshot.files
                if any(term in f.path.lower() or term in f.preview.lower() for term in terms)
            ]
            if matched:
                features.append(
                    {
                        "name": name,
                        "description": f"{name.title()} functionality present in the codebase",
                        "files": matched[:8],
                    }
                )
        return features

    def _local_issues(self, snapshot: ProjectSnapshot, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        issues = []
        if any(f["name"] == "testing" for f in features):
            test_files = [f.path for f in snapshot.files if f.category == "tests"]
            issues.append(
                {
                    "title": f"Expand test coverage for {snapshot.name}",
                    "body": (
                        f"## Context\n"
                        f"The project has test files including `{test_files[0] if test_files else 'tests/'}` "
                        f"but coverage should be expanded across core modules.\n\n"
                        f"## Tasks\n"
                        f"- [ ] Add integration tests for main workflows\n"
                        f"- [ ] Cover edge cases in service layer\n"
                        f"- [ ] Add CI test reporting"
                    ),
                    "labels": ["enhancement", "testing"],
                }
            )

        source_files = [f.path for f in snapshot.files if f.category == "source"]
        if source_files:
            issues.append(
                {
                    "title": f"Refactor core module `{source_files[0]}` for maintainability",
                    "body": (
                        f"## Problem\n"
                        f"`{source_files[0]}` has grown complex and would benefit from clearer separation "
                        f"of concerns.\n\n"
                        f"## Proposal\n"
                        f"- Extract reusable utilities\n"
                        f"- Improve error handling\n"
                        f"- Add inline documentation for public APIs"
                    ),
                    "labels": ["refactor"],
                }
            )

        if snapshot.dependencies:
            issues.append(
                {
                    "title": "Audit and update project dependencies",
                    "body": (
                        f"## Context\n"
                        f"Key dependencies include: {', '.join(snapshot.dependencies[:8])}.\n\n"
                        f"## Tasks\n"
                        f"- [ ] Check for security advisories\n"
                        f"- [ ] Update patch versions\n"
                        f"- [ ] Document upgrade notes"
                    ),
                    "labels": ["enhancement"],
                }
            )
        return issues[:5]

    def _local_pull_requests(
        self, snapshot: ProjectSnapshot, features: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        prs = []
        source_files = [f.path for f in snapshot.files if f.category == "source"]
        if source_files:
            prs.append(
                {
                    "title": f"Improve error handling in `{source_files[0]}`",
                    "body": (
                        f"## Summary\n"
                        f"This PR improves validation and error handling in `{source_files[0]}`.\n\n"
                        f"## Changes\n"
                        f"- Add input validation\n"
                        f"- Improve error messages\n"
                        f"- Add unit tests"
                    ),
                    "branch_name": "feature/error-handling",
                    "files": source_files[:3],
                    "labels": ["enhancement"],
                }
            )

        doc_files = [f.path for f in snapshot.files if f.category == "docs" or f.path.lower().endswith(".md")]
        if doc_files:
            prs.append(
                {
                    "title": "Update project documentation",
                    "body": (
                        f"## Summary\n"
                        f"Updates documentation including `{doc_files[0]}` with setup and usage details."
                    ),
                    "branch_name": "docs/update-readme",
                    "files": doc_files[:3],
                    "labels": ["documentation"],
                }
            )

        modules = self._group_modules(snapshot)
        for module in modules[:3]:
            files = module.get("files") or []
            if not files:
                continue
            name = module["name"]
            prs.append(
                {
                    "title": f"Refine `{name}` module implementation",
                    "body": (
                        f"## Summary\nImprove maintainability of the `{name}` module.\n\n"
                        f"## Files\n" + "\n".join(f"- `{f}`" for f in files[:5])
                    ),
                    "branch_name": f"refactor/{name.lower().replace(' ', '-')}",
                    "files": files[:3],
                    "labels": ["refactor"],
                }
            )

        test_files = [f.path for f in snapshot.files if f.category == "tests"]
        if test_files:
            prs.append(
                {
                    "title": "Expand automated test coverage",
                    "body": "## Summary\nAdd broader unit/integration coverage for critical paths.",
                    "branch_name": "feature/expand-tests",
                    "files": test_files[:3],
                    "labels": ["testing"],
                }
            )

        return prs[:6]
