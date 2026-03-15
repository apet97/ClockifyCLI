"""Tests for user operations."""

from __future__ import annotations

import json as jsonlib
import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, USER_ID, API_KEY, make_user,
)

USER_URL = f"{BASE_URL}/user"
USERS_URL = f"{BASE_URL}/workspaces/{WS_ID}/users"


@responses.activate
def test_get_current_user(backend):
    user = make_user()
    responses.add(responses.GET, USER_URL, json=user, status=200)
    result = backend.get_current_user()
    assert result["id"] == USER_ID
    assert result["email"] == "test@example.com"


@responses.activate
def test_list_workspace_users(backend):
    users = [make_user(USER_ID, "Alice"), make_user("user2", "Bob", "bob@example.com")]
    responses.add(
        responses.GET, USERS_URL,
        json=users, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = backend.list_users(WS_ID)
    assert len(result) == 2
    assert result[0]["name"] == "Alice"


# ── CLI tests ─────────────────────────────────────────────────────────

@responses.activate
def test_cli_users_me_json(runner, session):
    from cli_anything.clockify.clockify_cli import main

    user = make_user()
    responses.add(responses.GET, USER_URL, json=user, status=200)

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "users", "me", "--json",
    ])
    assert result.exit_code == 0
    data = jsonlib.loads(result.output)
    assert data["id"] == USER_ID


@responses.activate
def test_cli_timer_status_no_timer_json(runner, session):
    """timer status --json returns {running: false} when no timer running."""
    from cli_anything.clockify.clockify_cli import main

    responses.add(
        responses.GET, USER_URL,
        json=make_user(), status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE_URL}/workspaces/{WS_ID}/time-entries/status/in-progress",
        json=[], status=200,
        match_querystring=False,
    )

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "timer", "status", "--json",
    ])
    assert result.exit_code == 0
    data = jsonlib.loads(result.output)
    assert data["running"] is False


@responses.activate
def test_users_list_name_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, USERS_URL,
        json=[make_user(USER_ID, "Alice")],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "users", "list", "--name", "Alice", "--json"])
    assert result.exit_code == 0, result.output
    assert "name=Alice" in responses.calls[0].request.url


@responses.activate
def test_users_list_email_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, USERS_URL,
        json=[make_user(USER_ID, "Alice", "alice@example.com")],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "users", "list", "--email", "alice@example.com", "--json"])
    assert result.exit_code == 0, result.output
    assert "email=alice%40example.com" in responses.calls[0].request.url or "email=alice@example.com" in responses.calls[0].request.url


@responses.activate
def test_users_list_status_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, USERS_URL,
        json=[make_user()],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "users", "list", "--status", "ACTIVE", "--json"])
    assert result.exit_code == 0, result.output
    assert "status=ACTIVE" in responses.calls[0].request.url
