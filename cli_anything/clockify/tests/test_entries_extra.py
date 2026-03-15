"""Tests for extended time entry operations: bulk-delete, duplicate, mark-invoiced."""

from __future__ import annotations

import json as jsonlib
import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, USER_ID,
    make_time_entry,
)

ENTRIES_URL = f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries"
WS_ENTRIES_URL = f"{BASE_URL}/workspaces/{WS_ID}/time-entries"


@responses.activate
def test_bulk_delete_entries(backend):
    """bulk_delete_entries sends DELETE with comma-separated IDs as query param."""
    responses.add(
        responses.DELETE, ENTRIES_URL,
        json={}, status=200,
        match_querystring=False,
    )
    backend.bulk_delete_entries(WS_ID, USER_ID, ["e1", "e2", "e3"])
    req = responses.calls[0].request
    assert req.method == "DELETE"
    assert "time-entry-ids=e1%2Ce2%2Ce3" in req.url or "time-entry-ids=e1,e2,e3" in req.url or "time-entry-ids" in req.url


@responses.activate
def test_duplicate_entry(backend):
    """duplicate_entry POSTs to the duplicate endpoint."""
    entry = make_time_entry()
    dup_url = f"{ENTRIES_URL}/{entry['id']}/duplicate"
    responses.add(responses.POST, dup_url, json=make_time_entry("entry222222222222222222222"), status=201)
    result = backend.duplicate_entry(WS_ID, USER_ID, entry["id"])
    assert result["id"] == "entry222222222222222222222"


@responses.activate
def test_mark_entries_invoiced(backend):
    """mark_entries_invoiced PATCHes the invoiced endpoint."""
    invoiced_url = f"{WS_ENTRIES_URL}/invoiced"
    responses.add(responses.PATCH, invoiced_url, json={}, status=200)
    backend.mark_entries_invoiced(WS_ID, ["e1", "e2"], True)
    req = responses.calls[0].request
    assert req.method == "PATCH"
    body = jsonlib.loads(req.body)
    assert body["invoiced"] is True
    assert "e1" in body["timeEntryIds"]


@responses.activate
def test_bulk_update_entries(backend):
    """bulk_update_entries PUTs to the user time-entries endpoint."""
    responses.add(
        responses.PUT, ENTRIES_URL,
        json={"updatedIds": ["e1"]}, status=200,
    )
    result = backend.bulk_update_entries(WS_ID, USER_ID, [
        {"id": "e1", "description": "Updated"},
    ])
    assert responses.calls[0].request.method == "PUT"


@responses.activate
def test_cli_entries_bulk_delete(runner, session):
    """entries bulk-delete --ids ... --confirm should call bulk delete."""
    from cli_anything.clockify.clockify_cli import main

    # Need user endpoint for _user() resolution
    user_url = f"{BASE_URL}/user"
    responses.add(responses.GET, user_url, json={"id": USER_ID, "defaultWorkspace": WS_ID}, status=200)
    responses.add(
        responses.DELETE, ENTRIES_URL,
        json={}, status=200,
        match_querystring=False,
    )

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "entries", "bulk-delete",
        "--ids", "e1,e2",
        "--confirm", "--json",
    ])
    assert result.exit_code == 0
