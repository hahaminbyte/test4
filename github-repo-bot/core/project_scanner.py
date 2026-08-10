#!/usr/bin/env python3
"""Scan local project folders for AI analysis and history generation."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "env",
    ".env",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    "coverage",
    ".coverage",
    "htmlcov",
    ".idea",
    ".vscode",
    ".cursor",
    "vendor",
    ".tox",
}

SKIP_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".dylib",
    ".exe",
    ".bin",
    ".o",
    ".a",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".rar",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp4",
    ".mp3",
    ".lock",
}

MAX_FILE_BYTES = 64_000
MAX_FILES = 300
MAX_PREVIEW_LINES = 120

# Directories never copied into the published repo
SYNC_SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    "coverage",
    ".coverage",
    "htmlcov",
    ".idea",
    ".vscode",
    ".cursor",
    "vendor",
    ".tox",
    ".turbo",
    ".cache",
}

# Binary/junk extensions still skipped during analysis, but included when syncing the final tree
SYNC_SKIP_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".dylib",
    ".exe",
    ".o",
    ".a",
}


@dataclass
class ProjectFile:
    path: str
    size: int
    extension: str
    category: str
    preview: str
    content: str


@dataclass
class ProjectSnapshot:
    root: str
    name: str
    files: List[ProjectFile] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    detected_language: str = "unknown"
    detected_frameworks: List[str] = field(default_factory=list)
    file_count: int = 0
    total_bytes: int = 0

    def to_summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "root": self.root,
            "language": self.detected_language,
            "frameworks": self.detected_frameworks,
            "dependencies": self.dependencies,
            "file_count": self.file_count,
            "files": [
                {
                    "path": f.path,
                    "category": f.category,
                    "size": f.size,
                    "preview": f.preview[:2000],
                }
                for f in self.files
            ],
        }


class ProjectScanner:
    """Deep local scan of an existing project directory."""

    def __init__(self, project_path: str):
        self.root = Path(project_path).resolve()
        if not self.root.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        if not self.root.is_dir():
            raise NotADirectoryError(f"Project path is not a directory: {project_path}")

    def scan(self) -> ProjectSnapshot:
        files: List[ProjectFile] = []
        total_bytes = 0

        for file_path in self._iter_files():
            if len(files) >= MAX_FILES:
                break

            try:
                raw = file_path.read_bytes()
            except OSError:
                continue

            if len(raw) > MAX_FILE_BYTES:
                content = raw[:MAX_FILE_BYTES].decode("utf-8", errors="replace")
                content += "\n\n... [truncated for analysis] ..."
            else:
                content = raw.decode("utf-8", errors="replace")

            rel = str(file_path.relative_to(self.root))
            lines = content.splitlines()
            preview = "\n".join(lines[:MAX_PREVIEW_LINES])
            if len(lines) > MAX_PREVIEW_LINES:
                preview += "\n... [preview truncated] ..."

            category = self._categorize_file(rel)
            files.append(
                ProjectFile(
                    path=rel,
                    size=len(raw),
                    extension=file_path.suffix.lower(),
                    category=category,
                    preview=preview,
                    content=content,
                )
            )
            total_bytes += len(raw)

        files.sort(key=lambda f: (self._category_order(f.category), f.path))
        snapshot = ProjectSnapshot(
            root=str(self.root),
            name=self.root.name,
            files=files,
            file_count=len(files),
            total_bytes=total_bytes,
        )
        snapshot.dependencies = self._detect_dependencies(files)
        snapshot.detected_language = self._detect_language(files)
        snapshot.detected_frameworks = self._detect_frameworks(files, snapshot.dependencies)
        return snapshot

    def list_all_sync_files(self) -> List[str]:
        """Return every project-relative path that should be published to GitHub."""
        paths: List[str] = []
        for file_path in self._iter_sync_files():
            paths.append(str(file_path.relative_to(self.root)))
        return paths

    def _iter_sync_files(self):
        """Walk the full project for final publish (includes images/assets/lockfiles)."""
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = sorted(
                d for d in dirnames if d not in SYNC_SKIP_DIRS and d not in SKIP_DIRS
            )
            for filename in sorted(filenames):
                # Skip secret env files, keep examples/config dotfiles
                if filename == ".env" or filename.endswith(".env.local"):
                    continue
                path = Path(dirpath) / filename
                if path.suffix.lower() in SYNC_SKIP_EXTENSIONS:
                    continue
                if not path.is_file():
                    continue
                yield path

    def _iter_files(self):
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = sorted(
                d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
            )
            for filename in sorted(filenames):
                if filename.startswith(".") and filename not in {
                    ".gitignore",
                    ".env.example",
                    ".dockerignore",
                }:
                    continue
                path = Path(dirpath) / filename
                if path.suffix.lower() in SKIP_EXTENSIONS:
                    continue
                if not self._is_text_candidate(path):
                    continue
                yield path

    def _is_text_candidate(self, path: Path) -> bool:
        try:
            with open(path, "rb") as handle:
                chunk = handle.read(8192)
        except OSError:
            return False
        if b"\x00" in chunk:
            return False
        return True

    def _categorize_file(self, rel_path: str) -> str:
        lower = rel_path.lower()
        name = Path(lower).name

        if name in {
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "go.mod",
            "cargo.toml",
            "pom.xml",
            "build.gradle",
            "dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml",
            "makefile",
            "tsconfig.json",
            "webpack.config.js",
            "vite.config.ts",
        } or lower.endswith((".yaml", ".yml", ".toml", ".ini", ".cfg")):
            return "config"
        if any(part in lower for part in ("test", "spec", "__tests__", "tests/")):
            return "tests"
        if lower.endswith((".md", ".rst", ".txt")) or lower.startswith("docs/"):
            return "docs"
        if lower.endswith(
            (".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs", ".rb", ".php", ".cs", ".swift", ".kt")
        ):
            return "source"
        if lower.endswith((".html", ".css", ".scss", ".sass", ".less", ".vue", ".svelte")):
            return "frontend"
        if name in {".gitignore", "license", "readme.md"}:
            return "meta"
        return "other"

    def _category_order(self, category: str) -> int:
        return {
            "meta": 0,
            "config": 1,
            "source": 2,
            "frontend": 3,
            "tests": 4,
            "docs": 5,
            "other": 6,
        }.get(category, 7)

    def _detect_dependencies(self, files: List[ProjectFile]) -> List[str]:
        deps: List[str] = []

        for project_file in files:
            if project_file.path == "package.json":
                try:
                    data = json.loads(project_file.content)
                    deps.extend(data.get("dependencies", {}).keys())
                    deps.extend(data.get("devDependencies", {}).keys())
                except json.JSONDecodeError:
                    pass
            elif project_file.path == "requirements.txt":
                for line in project_file.content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        deps.append(line.split("==")[0].split(">=")[0].strip())
            elif project_file.path == "pyproject.toml":
                for line in project_file.content.splitlines():
                    if "=" in line and not line.strip().startswith("#"):
                        key = line.split("=")[0].strip().strip('"').strip("'")
                        if key and key.isidentifier():
                            deps.append(key)

        return sorted(set(deps))

    def _detect_language(self, files: List[ProjectFile]) -> str:
        counts: Dict[str, int] = {}
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
        }
        for project_file in files:
            if project_file.category not in {"source", "frontend", "tests"}:
                continue
            lang = mapping.get(project_file.extension)
            if lang:
                counts[lang] = counts.get(lang, 0) + 1
        if not counts:
            return "unknown"
        return max(counts, key=counts.get)

    def _detect_frameworks(self, files: List[ProjectFile], deps: List[str]) -> List[str]:
        dep_text = " ".join(deps).lower()
        file_text = " ".join(f.path.lower() for f in files)
        combined = dep_text + " " + file_text

        frameworks = []
        checks = [
            ("react", "react"),
            ("vue", "vue"),
            ("angular", "angular"),
            ("next", "next.js"),
            ("express", "express"),
            ("fastapi", "fastapi"),
            ("flask", "flask"),
            ("django", "django"),
            ("spring", "spring"),
            ("electron", "electron"),
            ("react-native", "react-native"),
        ]
        for needle, label in checks:
            if needle in combined:
                frameworks.append(label)
        return frameworks
