"""Tests for tag CRUD."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import BASE_URL, WS_ID, API_KEY, make_tag

TAGS_URL = f"{BASE_URL}/workspaces/{WS_ID}/tags"


@responses.activate
def test_list_tags(backend):
    tags = [make_tag("t1", "billable"), make_tag("t2", "internal")]
    responses.add(
        responses.GET, TAGS_URL,
        json=tags, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = backend.list_tags(WS_ID)
    assert len(result) == 2


@responses.activate
def test_create_tag(backend):
    tag = make_tag()
    responses.add(responses.POST, TAGS_URL, json=tag, status=201)
    result = backend.create_tag(WS_ID, {"name": "billable"})
    assert result["name"] == "billable"


@responses.activate
def test_update_tag(backend):
    tag_id = "tag1111111111111111111111"
    updated = make_tag(tag_id, "overhead")
    responses.add(responses.PUT, f"{TAGS_URL}/{tag_id}", json=updated, status=200)
    result = backend.update_tag(WS_ID, tag_id, {"name": "overhead"})
    assert result["name"] == "overhead"


@responses.activate
def test_delete_tag(backend):
    tag_id = "tag1111111111111111111111"
    responses.add(responses.DELETE, f"{TAGS_URL}/{tag_id}", json={}, status=200)
    result = backend.delete_tag(WS_ID, tag_id)
    assert isinstance(result, dict)


@responses.activate
def test_tags_list_name_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, TAGS_URL,
        json=[{"id": "t1", "name": "billable"}],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "tags", "list", "--name", "billable", "--json"])
    assert result.exit_code == 0, result.output
    assert "name=billable" in responses.calls[0].request.url


@responses.activate
def test_tags_list_archived_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, TAGS_URL,
        json=[{"id": "t1", "name": "old"}],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "tags", "list", "--archived", "--json"])
    assert result.exit_code == 0, result.output
    assert "archived=true" in responses.calls[0].request.url
