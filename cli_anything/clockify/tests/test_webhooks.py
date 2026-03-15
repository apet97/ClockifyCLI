"""Tests for webhook operations."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, API_KEY,
    make_webhook,
)

WEBHOOKS_URL = f"{BASE_URL}/workspaces/{WS_ID}/webhooks"


@responses.activate
def test_list_webhooks(backend):
    """list_webhooks returns a list."""
    hooks = [make_webhook("h1", "Hook 1"), make_webhook("h2", "Hook 2")]
    responses.add(responses.GET, WEBHOOKS_URL, json=hooks, status=200)
    result = backend.list_webhooks(WS_ID)
    assert len(result) == 2
    assert result[0]["name"] == "Hook 1"


@responses.activate
def test_create_webhook(backend):
    """create_webhook POSTs to correct URL and returns the webhook."""
    hook = make_webhook()
    responses.add(responses.POST, WEBHOOKS_URL, json=hook, status=201)
    result = backend.create_webhook(WS_ID, {
        "url": "https://example.com/hook",
        "name": "Test Hook",
        "triggerSourceType": "NEW_TIME_ENTRY",
    })
    assert result["id"] == hook["id"]
    req = responses.calls[0].request
    assert req.method == "POST"


@responses.activate
def test_get_webhook(backend):
    """get_webhook fetches by ID."""
    hook = make_webhook()
    responses.add(responses.GET, f"{WEBHOOKS_URL}/{hook['id']}", json=hook, status=200)
    result = backend.get_webhook(WS_ID, hook["id"])
    assert result["id"] == hook["id"]


@responses.activate
def test_delete_webhook(backend):
    """delete_webhook sends DELETE to correct URL."""
    hook_id = "hook111111111111111111111"
    responses.add(responses.DELETE, f"{WEBHOOKS_URL}/{hook_id}", json={}, status=200)
    backend.delete_webhook(WS_ID, hook_id)
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_get_webhook_logs(backend):
    """get_webhook_logs POSTs to the logs endpoint."""
    hook_id = "hook111111111111111111111"
    logs_url = f"{WEBHOOKS_URL}/{hook_id}/logs"
    responses.add(responses.POST, logs_url, json={"logs": []}, status=200)
    result = backend.get_webhook_logs(WS_ID, hook_id)
    assert responses.calls[0].request.method == "POST"


@responses.activate
def test_cli_webhooks_list_json(runner, session):
    """webhooks list --json returns JSON array."""
    from cli_anything.clockify.clockify_cli import main
    import json

    hooks = [make_webhook()]
    responses.add(responses.GET, WEBHOOKS_URL, json=hooks, status=200)

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "webhooks", "list", "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["name"] == "Test Hook"


@responses.activate
def test_webhooks_list_type_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, WEBHOOKS_URL,
        json=[make_webhook()],
        status=200,
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "webhooks", "list", "--type", "USER_CREATED", "--json"])
    assert result.exit_code == 0, result.output
    assert "type=USER_CREATED" in responses.calls[0].request.url
