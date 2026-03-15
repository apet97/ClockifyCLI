"""Tests for user group operations."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, USER_ID, API_KEY,
    make_group,
)

GROUPS_URL = f"{BASE_URL}/workspaces/{WS_ID}/user-groups"


@responses.activate
def test_list_groups(backend):
    """list_groups returns list."""
    groups = [make_group("g1", "Alpha"), make_group("g2", "Beta")]
    responses.add(responses.GET, GROUPS_URL, json=groups, status=200)
    result = backend.list_groups(WS_ID)
    assert len(result) == 2
    assert result[0]["name"] == "Alpha"


@responses.activate
def test_create_group(backend):
    """create_group POSTs to groups URL."""
    group = make_group()
    responses.add(responses.POST, GROUPS_URL, json=group, status=201)
    result = backend.create_group(WS_ID, {"name": "Test Group"})
    assert result["id"] == group["id"]


@responses.activate
def test_add_user_to_group(backend):
    """add_users_to_group POSTs to the group users URL."""
    group = make_group(user_ids=[USER_ID])
    url = f"{GROUPS_URL}/{group['id']}/users"
    responses.add(responses.POST, url, json=group, status=200)
    result = backend.add_users_to_group(WS_ID, group["id"], {"userIds": [USER_ID]})
    assert USER_ID in result["userIds"]


@responses.activate
def test_remove_user_from_group(backend):
    """remove_user_from_group DELETEs from the group users URL."""
    group_id = "grp1111111111111111111111"
    url = f"{GROUPS_URL}/{group_id}/users/{USER_ID}"
    responses.add(responses.DELETE, url, json={}, status=200)
    backend.remove_user_from_group(WS_ID, group_id, USER_ID)
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_delete_group(backend):
    """delete_group sends DELETE to correct URL."""
    group_id = "grp1111111111111111111111"
    responses.add(responses.DELETE, f"{GROUPS_URL}/{group_id}", json={}, status=200)
    backend.delete_group(WS_ID, group_id)
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_cli_groups_list_json(runner, session):
    """groups list --json returns JSON array."""
    from cli_anything.clockify.clockify_cli import main
    import json

    groups = [make_group()]
    responses.add(responses.GET, GROUPS_URL, json=groups, status=200)

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "groups", "list", "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1


@responses.activate
def test_groups_list_name_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    groups_url = f"{BASE_URL}/workspaces/{WS_ID}/user-groups"
    responses.add(
        responses.GET, groups_url,
        json=[make_group()],
        status=200,
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "groups", "list", "--name", "DevTeam", "--json"])
    assert result.exit_code == 0, result.output
    assert "name=DevTeam" in responses.calls[0].request.url


@responses.activate
def test_groups_list_project_id_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    groups_url = f"{BASE_URL}/workspaces/{WS_ID}/user-groups"
    responses.add(
        responses.GET, groups_url,
        json=[make_group()],
        status=200,
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "groups", "list", "--project-id", "proj123", "--json"])
    assert result.exit_code == 0, result.output
    assert "projectId=proj123" in responses.calls[0].request.url
