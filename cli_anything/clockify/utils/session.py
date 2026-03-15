"""Session management for the Clockify CLI.

Resolves credentials and workspace context from:
  1. CLI flags (passed in at runtime)
  2. Environment variables
  3. ~/.config/clockify-cli/config.json (or profiles/{name}.json)
  4. Error if not found
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".config" / "clockify-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_BASE_URL = "https://api.clockify.me/api/v1"
DEFAULT_REPORTS_URL = "https://reports.api.clockify.me/v1"


def _profile_config_file(profile: str = "default") -> Path:
    """Return config file path for a profile."""
    if profile == "default":
        return CONFIG_FILE
    return CONFIG_DIR / "profiles" / f"{profile}.json"


def load_config_file(profile: str = "default") -> dict:
    """Load config from profile-specific config file."""
    path = _profile_config_file(profile)
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config_file(data: dict, profile: str = "default") -> None:
    """Persist config to disk for a specific profile (owner-only permissions)."""
    path = _profile_config_file(profile)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    existing = load_config_file(profile)
    existing.update(data)
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(existing, f, indent=2)


@dataclass
class Session:
    """Resolved runtime session configuration.

    Fields are resolved lazily in priority order:
      CLI flag → env var → config file → error.
    """

    api_key: str
    workspace_id: Optional[str] = None
    base_url: str = DEFAULT_BASE_URL
    reports_url: str = DEFAULT_REPORTS_URL
    # Lazily resolved on first use
    _user_id: Optional[str] = field(default=None, repr=False)

    @property
    def user_id(self) -> Optional[str]:
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        self._user_id = value

    @classmethod
    def resolve(
        cls,
        api_key: Optional[str] = None,
        workspace_id: Optional[str] = None,
        base_url: Optional[str] = None,
        reports_url: Optional[str] = None,
        profile: str = "default",
    ) -> "Session":
        """Build a Session by resolving each field from available sources."""
        cfg = load_config_file(profile)

        resolved_key = (
            api_key
            or os.environ.get("CLOCKIFY_API_KEY")
            or cfg.get("api_key")
        )
        if not resolved_key:
            raise ValueError(
                "No API key found. Set CLOCKIFY_API_KEY env var, "
                "pass --api-key, or add api_key to ~/.config/clockify-cli/config.json"
            )

        resolved_ws = (
            workspace_id
            or os.environ.get("CLOCKIFY_WORKSPACE_ID")
            or cfg.get("workspace_id")
        )

        resolved_base = (
            base_url
            or os.environ.get("CLOCKIFY_BASE_URL")
            or cfg.get("base_url")
            or DEFAULT_BASE_URL
        )

        resolved_reports = (
            reports_url
            or os.environ.get("CLOCKIFY_REPORTS_URL")
            or cfg.get("reports_url")
            or DEFAULT_REPORTS_URL
        )

        return cls(
            api_key=resolved_key,
            workspace_id=resolved_ws,
            base_url=resolved_base.rstrip("/"),
            reports_url=resolved_reports.rstrip("/"),
        )

    def resolve_workspace(self, backend: object) -> str:
        """Return workspace_id, auto-resolving from API if not set.

        If exactly one workspace exists, uses it automatically.
        If multiple exist, raises an error listing options.
        """
        if self.workspace_id:
            return self.workspace_id

        workspaces = backend.list_workspaces()  # type: ignore[attr-defined]
        if not workspaces:
            raise ValueError(
                "No workspaces found for this API key. "
                "Create a workspace at https://clockify.me or check your API key."
            )
        if len(workspaces) == 1:
            self.workspace_id = workspaces[0]["id"]
            return self.workspace_id

        ws_list = "\n".join(
            f"  {w['id']}  {w.get('name', '')}" for w in workspaces
        )
        raise ValueError(
            f"Multiple workspaces found. Set CLOCKIFY_WORKSPACE_ID or use "
            f"'clockify workspaces use <id>':\n{ws_list}"
        )

    def resolve_user(self, backend: object) -> str:
        """Return user_id, fetching from API on first call and caching."""
        if not self._user_id:
            user = backend.get_current_user()  # type: ignore[attr-defined]
            uid = user.get("id") if isinstance(user, dict) else None
            if not uid:
                raise ValueError("Failed to resolve user ID from API response")
            self._user_id = uid
        return self._user_id
