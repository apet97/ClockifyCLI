"""Tests for workspace operations."""

from __future__ import annotations

import json as jsonlib
import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, make_workspace,
)

WORKSPACES_URL = f"{BASE_URL}/workspaces"


@responses.activate
def test_list_workspaces(backend):
    workspaces = [make_workspace(WS_ID, "My Workspace")]
    responses.add(responses.GET, WORKSPACES_URL, json=workspaces, status=200)
    result = backend.list_workspaces()
    assert len(result) == 1
    assert result[0]["id"] == WS_ID


@responses.activate
def test_get_workspace(backend):
    ws = make_workspace()
    responses.add(responses.GET, f"{WORKSPACES_URL}/{WS_ID}", json=ws, status=200)
    result = backend.get_workspace(WS_ID)
    assert result["id"] == WS_ID


# ── CLI tests ─────────────────────────────────────────────────────────

@responses.activate
def test_cli_workspaces_list_json(runner, session):
    from cli_anything.clockify.clockify_cli import main

    workspaces = [make_workspace()]
    responses.add(responses.GET, WORKSPACES_URL, json=workspaces, status=200)

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "workspaces", "list", "--json",
    ])
    assert result.exit_code == 0
    data = jsonlib.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["id"] == WS_ID


@responses.activate
def test_cli_workspaces_use(runner, session, tmp_path, monkeypatch):
    """workspaces use should save workspace_id to config."""
    from cli_anything.clockify.clockify_cli import main
    import cli_anything.clockify.utils.session as session_mod

    # Redirect config to tmp_path
    monkeypatch.setattr(session_mod, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(session_mod, "CONFIG_FILE", tmp_path / "config.json")

    new_ws = "ws999999999999999999999999"
    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "workspaces", "use", new_ws, "--json",
    ])
    assert result.exit_code == 0
    data = jsonlib.loads(result.output)
    assert data["workspace_id"] == new_ws
    assert data["saved"] is True
