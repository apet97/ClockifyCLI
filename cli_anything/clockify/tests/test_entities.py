"""Tests for entity change tracking operations."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID,
)

ENTITIES_CREATED_URL = f"{BASE_URL}/workspaces/{WS_ID}/entities/created"
ENTITIES_DELETED_URL = f"{BASE_URL}/workspaces/{WS_ID}/entities/deleted"
ENTITIES_UPDATED_URL = f"{BASE_URL}/workspaces/{WS_ID}/entities/updated"


def make_entity_change(
    entity_id: str = "ent1111111111111111111111",
    entity_type: str = "TIME_ENTRY",
    changed_at: str = "2026-03-13T10:00:00Z",
) -> dict:
    return {
        "id": entity_id,
        "entityType": entity_type,
        "changedAt": changed_at,
    }


@responses.activate
def test_list_created_entities(backend):
    """list_created_entities GETs the created endpoint with type param."""
    entities = [make_entity_change()]
    responses.add(
        responses.GET, ENTITIES_CREATED_URL,
        json=entities, status=200,
        match_querystring=False,
    )
    result = backend.list_created_entities(
        WS_ID, "TIME_ENTRY",
        "2026-03-01T00:00:00Z",
        "2026-03-13T23:59:59Z",
    )
    assert len(result) == 1
    req = responses.calls[0].request
    assert "type=TIME_ENTRY" in req.url
    assert "start=" in req.url


@responses.activate
def test_list_deleted_entities(backend):
    """list_deleted_entities GETs the deleted endpoint."""
    entities = [make_entity_change("e2")]
    responses.add(
        responses.GET, ENTITIES_DELETED_URL,
        json=entities, status=200,
        match_querystring=False,
    )
    result = backend.list_deleted_entities(
        WS_ID, "PROJECT",
        "2026-03-01T00:00:00Z",
        "2026-03-13T23:59:59Z",
    )
    assert len(result) == 1
    req = responses.calls[0].request
    assert "type=PROJECT" in req.url


@responses.activate
def test_list_updated_entities(backend):
    """list_updated_entities GETs the updated endpoint."""
    entities = [make_entity_change("e3"), make_entity_change("e4")]
    responses.add(
        responses.GET, ENTITIES_UPDATED_URL,
        json=entities, status=200,
        match_querystring=False,
    )
    result = backend.list_updated_entities(
        WS_ID, "TIME_ENTRY",
        "2026-03-01T00:00:00Z",
        "2026-03-13T23:59:59Z",
    )
    assert len(result) == 2


@responses.activate
def test_cli_entities_created_json(runner, session):
    """entities created --type ... returns JSON array."""
    from cli_anything.clockify.clockify_cli import main
    import json

    entities = [make_entity_change()]
    responses.add(
        responses.GET, ENTITIES_CREATED_URL,
        json=entities, status=200,
        match_querystring=False,
    )

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "entities", "created",
        "--type", "TIME_ENTRY",
        "--start", "2026-03-01",
        "--end", "2026-03-13",
        "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["entityType"] == "TIME_ENTRY"
