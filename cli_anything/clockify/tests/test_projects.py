"""Tests for project operations."""

from __future__ import annotations

import json as jsonlib
import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, API_KEY, make_project,
)

PROJECTS_URL = f"{BASE_URL}/workspaces/{WS_ID}/projects"


@responses.activate
def test_list_projects_pagination(backend):
    """list_projects should collect all pages."""
    page1 = [make_project("p1", "Alpha"), make_project("p2", "Beta")]
    page2 = [make_project("p3", "Gamma")]

    responses.add(
        responses.GET, PROJECTS_URL,
        json=page1, status=200,
        headers={"Last-Page": "false"},
        match_querystring=False,
    )
    responses.add(
        responses.GET, PROJECTS_URL,
        json=page2, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = backend.list_projects(WS_ID, page_size=2)
    assert len(result) == 3


@responses.activate
def test_list_projects_name_filter(backend):
    """list_projects with name= sends name as query param."""
    responses.add(
        responses.GET, PROJECTS_URL,
        json=[make_project(name="My Project")], status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = backend.list_projects(WS_ID, name="My Project")
    assert len(result) == 1
    req = responses.calls[0].request
    assert "name=My+Project" in req.url or "name=My%20Project" in req.url or "name=" in req.url


@responses.activate
def test_archived_filter_sent(backend):
    """archived filter should appear as query param."""
    responses.add(
        responses.GET, PROJECTS_URL,
        json=[], status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    backend.list_projects(WS_ID, archived=True)
    req = responses.calls[0].request
    assert "archived=true" in req.url


@responses.activate
def test_create_project(backend):
    p = make_project()
    responses.add(responses.POST, PROJECTS_URL, json=p, status=201)
    result = backend.create_project(WS_ID, {"name": "New Project", "color": "#FF0000"})
    assert result["id"] == p["id"]


@responses.activate
def test_delete_project(backend):
    proj_id = "proj111111111111111111111"
    url = f"{PROJECTS_URL}/{proj_id}"
    responses.add(responses.DELETE, url, json={}, status=200)
    backend.delete_project(WS_ID, proj_id)


# ── CLI: name→ID resolution ───────────────────────────────────────────

@responses.activate
def test_cli_projects_list_json(runner, session):
    """projects list --json returns JSON array."""
    from cli_anything.clockify.clockify_cli import main
    import json

    projects = [make_project("p1", "Alpha"), make_project("p2", "Beta")]
    responses.add(
        responses.GET, PROJECTS_URL,
        json=projects, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "projects", "list", "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 2
    assert data[0]["name"] == "Alpha"


@responses.activate
def test_projects_list_billable_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, PROJECTS_URL,
        json=[make_project()],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "projects", "list", "--billable", "--json"])
    assert result.exit_code == 0, result.output
    assert "billable=true" in responses.calls[0].request.url


@responses.activate
def test_projects_list_client_id_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, PROJECTS_URL,
        json=[make_project()],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "projects", "list", "--client-id", "client123", "--json"])
    assert result.exit_code == 0, result.output
    assert "clients=client123" in responses.calls[0].request.url


@responses.activate
def test_projects_list_sort_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, PROJECTS_URL,
        json=[make_project()],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "projects", "list", "--sort-column", "NAME", "--sort-order", "ASCENDING", "--json"])
    assert result.exit_code == 0, result.output
    assert "sort-column=NAME" in responses.calls[0].request.url
