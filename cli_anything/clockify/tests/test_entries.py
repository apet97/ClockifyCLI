"""Tests for time entry CRUD."""

from __future__ import annotations

import json as jsonlib
import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, USER_ID, API_KEY, make_time_entry,
)


ENTRIES_URL = f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries"
ENTRY_URL_TMPL = f"{BASE_URL}/workspaces/{WS_ID}/time-entries/{{id}}"


@responses.activate
def test_list_entries_with_filters(backend):
    """list_entries should pass start/end/project as query params."""
    entries = [make_time_entry()]
    responses.add(
        responses.GET, ENTRIES_URL,
        json=entries, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = backend.list_entries(
        WS_ID, USER_ID,
        start="2026-03-01T00:00:00Z",
        end="2026-03-13T23:59:59Z",
    )
    assert len(result) == 1
    req = responses.calls[0].request
    assert "start=" in req.url
    assert "end=" in req.url


@responses.activate
def test_create_entry(backend):
    """create_entry sends correct body."""
    entry = make_time_entry()
    responses.add(responses.POST, ENTRIES_URL, json=entry, status=201)
    body = {
        "start": "2026-03-13T09:00:00Z",
        "end": "2026-03-13T10:00:00Z",
        "description": "Test work",
    }
    result = backend.create_entry(WS_ID, USER_ID, body)
    assert result["id"] == entry["id"]

    req_body = jsonlib.loads(responses.calls[0].request.body)
    assert req_body["start"] == "2026-03-13T09:00:00Z"
    assert req_body["description"] == "Test work"


@responses.activate
def test_get_entry(backend):
    entry = make_time_entry()
    url = ENTRY_URL_TMPL.format(id=entry["id"])
    responses.add(responses.GET, url, json=entry, status=200)
    result = backend.get_entry(WS_ID, entry["id"])
    assert result["id"] == entry["id"]


@responses.activate
def test_update_entry(backend):
    entry = make_time_entry()
    url = ENTRY_URL_TMPL.format(id=entry["id"])
    updated = dict(entry)
    updated["description"] = "Updated work"
    responses.add(responses.PUT, url, json=updated, status=200)
    result = backend.update_entry(WS_ID, entry["id"], updated)
    assert result["description"] == "Updated work"


@responses.activate
def test_delete_entry(backend):
    entry_id = "entry111111111111111111111"
    url = ENTRY_URL_TMPL.format(id=entry_id)
    responses.add(responses.DELETE, url, json={}, status=200)
    result = backend.delete_entry(WS_ID, entry_id)
    assert isinstance(result, dict)


# ── CLI tests ─────────────────────────────────────────────────────────

@responses.activate
def test_cli_entries_today_json(runner, session):
    """entries today --json should return a JSON array."""
    from cli_anything.clockify.clockify_cli import main

    entries = [make_time_entry()]
    user_url = f"{BASE_URL}/user"
    entries_url = ENTRIES_URL

    responses.add(responses.GET, user_url, json={"id": USER_ID, "defaultWorkspace": WS_ID}, status=200)
    responses.add(
        responses.GET, entries_url,
        json=entries, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "entries", "today", "--json",
    ])
    assert result.exit_code == 0
    data = jsonlib.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["id"] == entries[0]["id"]


@responses.activate
def test_entries_list_task_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    user_url = f"{BASE_URL}/user"
    responses.add(responses.GET, user_url, json={"id": USER_ID, "defaultWorkspace": WS_ID}, status=200)
    responses.add(
        responses.GET, ENTRIES_URL,
        json=[make_time_entry()],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "entries", "list", "--task", "task123", "--json"])
    assert result.exit_code == 0, result.output
    assert "task=task123" in responses.calls[-1].request.url


@responses.activate
def test_entries_list_description_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    user_url = f"{BASE_URL}/user"
    responses.add(responses.GET, user_url, json={"id": USER_ID, "defaultWorkspace": WS_ID}, status=200)
    responses.add(
        responses.GET, ENTRIES_URL,
        json=[make_time_entry()],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "entries", "list", "--description", "Coding", "--json"])
    assert result.exit_code == 0, result.output
    assert "description=Coding" in responses.calls[-1].request.url


@responses.activate
def test_entries_list_in_progress_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    user_url = f"{BASE_URL}/user"
    responses.add(responses.GET, user_url, json={"id": USER_ID, "defaultWorkspace": WS_ID}, status=200)
    responses.add(
        responses.GET, ENTRIES_URL,
        json=[make_time_entry()],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "entries", "list", "--in-progress", "--json"])
    assert result.exit_code == 0, result.output
    assert "in-progress=true" in responses.calls[-1].request.url
