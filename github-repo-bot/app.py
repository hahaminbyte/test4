#!/usr/bin/env python3
"""
GitHub Repository Enhancement Bot - Web UI
Analyze existing local projects with AI and publish contextual history to GitHub.
"""

from __future__ import annotations

import json
import os
import secrets
import threading
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from core.project_bot import ProjectBot

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

operations: Dict[str, Dict[str, Any]] = {}
ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")


def _load_default_team() -> list:
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as handle:
            return json.load(handle).get("developers", [])
    return []


def _mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def _normalize_secret(value: Optional[str]) -> str:
    """Strip whitespace/quotes that break GitHub auth."""
    if not value:
        return ""
    token = value.strip()
    if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
        token = token[1:-1].strip()
    # Common paste artifacts
    token = token.replace("\n", "").replace("\r", "").replace(" ", "")
    return token


def _validate_github_token(token: str) -> Dict[str, Any]:
    """Verify a GitHub token against the API."""
    token = _normalize_secret(token)
    if not token:
        return {"valid": False, "error": "GitHub token is empty. Paste a token from https://github.com/settings/tokens"}

    if token in {"ghp_xxxxxxxxxxxx", "ghp_your_token_here", "your_github_token"}:
        return {"valid": False, "error": "That looks like a placeholder token. Paste your real GitHub PAT."}

    if not (token.startswith("ghp_") or token.startswith("github_pat_") or token.startswith("gho_")):
        return {
            "valid": False,
            "error": (
                "Token format looks wrong. Classic PATs start with ghp_, "
                "fine-grained PATs start with github_pat_."
            ),
        }

    try:
        from github import Github
        from github.GithubException import BadCredentialsException, GithubException

        gh = Github(token)
        user = gh.get_user()
        login = user.login
        # Touch rate limit to confirm auth works
        _ = gh.get_rate_limit()
        return {
            "valid": True,
            "login": login,
            "token_type": "fine-grained" if token.startswith("github_pat_") else "classic",
            "message": f"Authenticated as @{login}",
        }
    except Exception as exc:
        message = str(exc)
        if "401" in message or "Bad credentials" in message:
            return {
                "valid": False,
                "error": (
                    "GitHub rejected this token (401 Bad credentials). "
                    "Create a new token at https://github.com/settings/tokens "
                    "with 'repo' scope (classic) or Contents+Metadata+Pull requests+Issues "
                    "permissions (fine-grained), then paste it again and click Save to .env."
                ),
            }
        return {"valid": False, "error": f"Token check failed: {message}"}


def _write_env_value(key: str, value: str) -> None:
    """Update or append a key in the local .env file."""
    lines: list[str] = []
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, encoding="utf-8") as handle:
            lines = handle.read().splitlines()

    updated = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{key}=") and not line.strip().startswith("#"):
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"{key}={value}")

    with open(ENV_FILE, "w", encoding="utf-8") as handle:
        handle.write("\n".join(new_lines).rstrip() + "\n")


def _publish_async(config: Dict[str, Any], operation_id: str) -> None:
    try:
        def update_progress(status: str, progress: int) -> None:
            operations[operation_id] = {
                **operations.get(operation_id, {}),
                "status": status,
                "progress": progress,
            }

        operations[operation_id] = {"status": "initializing", "progress": 0}

        github_token = _normalize_secret(config.get("github_token") or os.getenv("GITHUB_TOKEN"))
        openai_api_key = _normalize_secret(config.get("openai_api_key") or os.getenv("OPENAI_API_KEY"))

        auth = _validate_github_token(github_token)
        if not auth.get("valid"):
            raise RuntimeError(auth.get("error") or "Invalid GitHub token")

        update_progress("authenticated", 3)

        bot = ProjectBot(
            github_token=github_token,
            openai_api_key=openai_api_key,
            openai_model=config.get("openai_model") or os.getenv("OPENAI_MODEL"),
        )

        result = bot.publish_project(
            project_path=config["project_path"],
            repo_name=config["repo_name"],
            config=config,
            progress_callback=update_progress,
        )

        operations[operation_id] = {
            "status": "completed",
            "progress": 100,
            "repository_url": result["repository_url"],
            "commits_created": result["commits_created"],
            "issues_created": result["issues_created"],
            "pull_requests_created": result["pull_requests_created"],
            "pull_requests_merged": result.get("pull_requests_merged", 0),
            "achievements": result.get("achievements"),
            "analysis_summary": result.get("analysis_summary", ""),
            "ai_powered": result.get("ai_powered", False),
            "message": (
                f"Published {result['commits_created']} contextual commits, "
                f"{result['issues_created']} issues, and "
                f"{result['pull_requests_created']} pull requests "
                f"({result.get('pull_requests_merged', 0)} merged)."
                + (
                    f" Achievements: {', '.join(result['achievements'].get('earned', [])) or 'none'}."
                    if result.get("achievements")
                    else ""
                )
            ),
        }
    except Exception as exc:
        operations[operation_id] = {
            "status": "error",
            "progress": 0,
            "message": str(exc),
        }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/settings", methods=["GET"])
def get_settings():
    """Return current credential status and defaults for the UI."""
    github_token = os.getenv("GITHUB_TOKEN", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    return jsonify(
        {
            "github_token_set": bool(github_token),
            "github_token_masked": _mask_secret(github_token),
            "openai_api_key_set": bool(openai_key),
            "openai_api_key_masked": _mask_secret(openai_key),
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "default_commits": int(os.getenv("DEFAULT_COMMITS", "50")),
            "default_days_back": int(os.getenv("DEFAULT_DAYS_BACK", "90")),
            "default_private": os.getenv("DEFAULT_PRIVATE", "true").lower() == "true",
            "cwd": os.getcwd(),
        }
    )


@app.route("/api/settings", methods=["POST"])
def save_settings():
    """Save credentials from the UI into .env and process env."""
    data = request.json or {}
    saved = []

    github_token = _normalize_secret(data.get("github_token"))
    openai_api_key = _normalize_secret(data.get("openai_api_key"))
    openai_model = (data.get("openai_model") or "").strip() or "gpt-4o-mini"

    github_login = None
    if github_token:
        auth = _validate_github_token(github_token)
        if not auth.get("valid"):
            return jsonify({"error": auth.get("error"), "valid": False}), 400
        github_login = auth.get("login")
        os.environ["GITHUB_TOKEN"] = github_token
        _write_env_value("GITHUB_TOKEN", github_token)
        saved.append("GITHUB_TOKEN")

    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        _write_env_value("OPENAI_API_KEY", openai_api_key)
        saved.append("OPENAI_API_KEY")

    if openai_model:
        os.environ["OPENAI_MODEL"] = openai_model
        _write_env_value("OPENAI_MODEL", openai_model)
        saved.append("OPENAI_MODEL")

    if not saved:
        return jsonify({"error": "No settings provided to save"}), 400

    return jsonify(
        {
            "success": True,
            "saved": saved,
            "message": f"Saved {', '.join(saved)} to .env"
            + (f" (GitHub user: @{github_login})" if github_login else ""),
            "github_token_set": bool(os.getenv("GITHUB_TOKEN")),
            "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        }
    )


@app.route("/api/validate-github-token", methods=["POST"])
def validate_github_token_endpoint():
    data = request.json or {}
    token = _normalize_secret(data.get("github_token") or os.getenv("GITHUB_TOKEN"))
    result = _validate_github_token(token)
    status = 200 if result.get("valid") else 400
    return jsonify(result), status


@app.route("/api/create-repository", methods=["POST"])
def create_repository():
    config = request.json or {}
    operation_id = secrets.token_urlsafe(16)

    # Fall back to saved env credentials when UI fields are empty
    config["github_token"] = _normalize_secret(
        config.get("github_token") or os.getenv("GITHUB_TOKEN", "")
    )
    config["openai_api_key"] = _normalize_secret(
        config.get("openai_api_key") or os.getenv("OPENAI_API_KEY", "")
    )
    if not config.get("openai_model"):
        config["openai_model"] = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    required = ["github_token", "repo_name", "project_path"]
    for field in required:
        if not config.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    auth = _validate_github_token(config["github_token"])
    if not auth.get("valid"):
        return jsonify({"error": auth.get("error")}), 401

    if not config.get("team_members"):
        config["team_members"] = _load_default_team()

    thread = threading.Thread(target=_publish_async, args=(config, operation_id))
    thread.start()

    return jsonify({"operation_id": operation_id, "github_user": auth.get("login")})


@app.route("/api/browse-folders", methods=["POST"])
def browse_folders():
    """List subdirectories for the project path picker."""
    data = request.json or {}
    path = (data.get("path") or os.path.expanduser("~")).strip()
    path = os.path.abspath(os.path.expanduser(path))

    if not os.path.isdir(path):
        return jsonify({"error": f"Not a directory: {path}"}), 400

    try:
        entries = []
        for name in sorted(os.listdir(path)):
            full = os.path.join(path, name)
            if os.path.isdir(full) and not name.startswith("."):
                entries.append({"name": name, "path": full})

        parent = os.path.dirname(path)
        return jsonify(
            {
                "current": path,
                "parent": parent if parent != path else None,
                "folders": entries[:200],
            }
        )
    except PermissionError:
        return jsonify({"error": f"Permission denied: {path}"}), 403


@app.route("/api/validate-project", methods=["POST"])
def validate_project():
    data = request.json or {}
    project_path = data.get("project_path", "").strip()

    if not project_path:
        return jsonify({"error": "project_path is required"}), 400

    try:
        bot = ProjectBot(github_token=data.get("github_token") or os.getenv("GITHUB_TOKEN") or "dummy")
        preview = bot.validate_project_path(project_path)
        return jsonify(preview)
    except Exception as exc:
        return jsonify({"valid": False, "error": str(exc)}), 400


@app.route("/api/achievements", methods=["GET"])
def list_achievements():
    from core.achievement_unlocker import describe_badges

    return jsonify({"badges": describe_badges()})


@app.route("/api/unlock-achievements", methods=["POST"])
def unlock_achievements_endpoint():
    """Run achievement unlocker on an existing GitHub repo (no local project required)."""
    data = request.json or {}
    operation_id = secrets.token_urlsafe(16)

    github_token = _normalize_secret(data.get("github_token") or os.getenv("GITHUB_TOKEN", ""))
    repo_name = (data.get("repo_name") or "").strip()
    if not github_token or not repo_name:
        return jsonify({"error": "github_token and repo_name are required"}), 400

    auth = _validate_github_token(github_token)
    if not auth.get("valid"):
        return jsonify({"error": auth.get("error")}), 401

    def _run():
        try:
            from core.achievement_unlocker import AchievementUnlocker, SUPPORTED_BADGES

            operations[operation_id] = {"status": "unlocking_achievements", "progress": 10}

            def update(status: str, progress: int) -> None:
                operations[operation_id] = {
                    **operations.get(operation_id, {}),
                    "status": status,
                    "progress": progress,
                }

            unlocker = AchievementUnlocker(github_token, team_members=_load_default_team())
            result = unlocker.unlock(
                repo_name=repo_name,
                badges=data.get("achievement_badges") or SUPPORTED_BADGES,
                pull_shark_count=int(data.get("pull_shark_count", 16)),
                pair_count=int(data.get("pair_count", 10)),
                reaction_rounds=int(data.get("reaction_rounds", 20)),
                delay_seconds=float(data.get("achievement_delay", 2.0)),
                progress_callback=update,
            )
            operations[operation_id] = {
                "status": "completed",
                "progress": 100,
                "repository_url": result.get("repository"),
                "achievements": result,
                "message": (
                    f"Achievement run finished. Earned/attempted: "
                    f"{', '.join(result.get('earned') or []) or 'none'}."
                ),
            }
        except Exception as exc:
            operations[operation_id] = {"status": "error", "progress": 0, "message": str(exc)}

    threading.Thread(target=_run).start()
    return jsonify({"operation_id": operation_id, "github_user": auth.get("login")})


@app.route("/api/status/<operation_id>")
def get_status(operation_id: str):
    if operation_id in operations:
        return jsonify(operations[operation_id])
    return jsonify({"error": "Operation not found"}), 404


if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
