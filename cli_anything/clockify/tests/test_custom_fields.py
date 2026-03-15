"""Tests for custom field operations."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID,
)

FIELDS_URL = f"{BASE_URL}/workspaces/{WS_ID}/custom-fields"
PROJ_ID = "proj111111111111111111111"


def make_custom_field(
    field_id: str = "cf11111111111111111111111",
    name: str = "Ticket #",
    field_type: str = "TXT",
) -> dict:
    return {
        "id": field_id,
        "name": name,
        "type": field_type,
        "status": "ACTIVE",
        "workspaceId": WS_ID,
    }


@responses.activate
def test_list_custom_fields(backend):
    """list_custom_fields returns list."""
    fields = [make_custom_field("f1", "Ticket"), make_custom_field("f2", "Budget")]
    responses.add(responses.GET, FIELDS_URL, json=fields, status=200)
    result = backend.list_custom_fields(WS_ID)
    assert len(result) == 2
    assert result[0]["name"] == "Ticket"


@responses.activate
def test_create_custom_field(backend):
    """create_custom_field POSTs to custom-fields URL."""
    field = make_custom_field()
    responses.add(responses.POST, FIELDS_URL, json=field, status=201)
    result = backend.create_custom_field(WS_ID, {"name": "Ticket #", "type": "TXT"})
    assert result["id"] == field["id"]


@responses.activate
def test_delete_custom_field(backend):
    """delete_custom_field sends DELETE to correct URL."""
    field_id = "cf11111111111111111111111"
    responses.add(responses.DELETE, f"{FIELDS_URL}/{field_id}", json={}, status=200)
    backend.delete_custom_field(WS_ID, field_id)
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_list_project_custom_fields(backend):
    """list_project_custom_fields GETs project-level custom fields."""
    proj_fields_url = f"{BASE_URL}/workspaces/{WS_ID}/projects/{PROJ_ID}/custom-fields"
    fields = [make_custom_field()]
    responses.add(responses.GET, proj_fields_url, json=fields, status=200)
    result = backend.list_project_custom_fields(WS_ID, PROJ_ID)
    assert len(result) == 1


@responses.activate
def test_delete_project_custom_field(backend):
    """delete_project_custom_field sends DELETE to project custom field URL."""
    field_id = "cf11111111111111111111111"
    url = f"{BASE_URL}/workspaces/{WS_ID}/projects/{PROJ_ID}/custom-fields/{field_id}"
    responses.add(responses.DELETE, url, json={}, status=200)
    backend.delete_project_custom_field(WS_ID, PROJ_ID, field_id)
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_cli_custom_fields_list_json(runner, session):
    """custom-fields list --json returns JSON array."""
    from cli_anything.clockify.clockify_cli import main
    import json

    fields = [make_custom_field()]
    responses.add(responses.GET, FIELDS_URL, json=fields, status=200)

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "custom-fields", "list", "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["name"] == "Ticket #"
