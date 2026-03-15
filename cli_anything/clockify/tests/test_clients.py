"""Tests for client CRUD."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import BASE_URL, WS_ID, API_KEY, make_client

CLIENTS_URL = f"{BASE_URL}/workspaces/{WS_ID}/clients"


@responses.activate
def test_list_clients(backend):
    clients = [make_client("c1", "ACME"), make_client("c2", "Globex")]
    responses.add(
        responses.GET, CLIENTS_URL,
        json=clients, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = backend.list_clients(WS_ID)
    assert len(result) == 2
    assert result[0]["name"] == "ACME"


@responses.activate
def test_create_client(backend):
    client = make_client()
    responses.add(responses.POST, CLIENTS_URL, json=client, status=201)
    result = backend.create_client(WS_ID, {"name": "Test Client"})
    assert result["name"] == "Test Client"


@responses.activate
def test_update_client(backend):
    client_id = "client11111111111111111111"
    updated = make_client(client_id, "Renamed Client")
    responses.add(responses.PUT, f"{CLIENTS_URL}/{client_id}", json=updated, status=200)
    result = backend.update_client(WS_ID, client_id, {"name": "Renamed Client"})
    assert result["name"] == "Renamed Client"


@responses.activate
def test_delete_client(backend):
    client_id = "client11111111111111111111"
    responses.add(responses.DELETE, f"{CLIENTS_URL}/{client_id}", json={}, status=200)
    result = backend.delete_client(WS_ID, client_id)
    assert isinstance(result, dict)


@responses.activate
def test_clients_list_name_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, CLIENTS_URL,
        json=[{"id": "c1", "name": "Acme"}],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "clients", "list", "--name", "Acme", "--json"])
    assert result.exit_code == 0, result.output
    assert "name=Acme" in responses.calls[0].request.url


@responses.activate
def test_clients_list_archived_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, CLIENTS_URL,
        json=[{"id": "c1", "name": "Old Client"}],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "clients", "list", "--archived", "--json"])
    assert result.exit_code == 0, result.output
    assert "archived=true" in responses.calls[0].request.url
