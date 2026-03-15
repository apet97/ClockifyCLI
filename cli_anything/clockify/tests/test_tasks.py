"""Tests for task CRUD."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import BASE_URL, WS_ID, API_KEY, make_task, make_project

PROJ_ID = "proj111111111111111111111"
TASKS_URL = f"{BASE_URL}/workspaces/{WS_ID}/projects/{PROJ_ID}/tasks"
PROJECTS_URL = f"{BASE_URL}/workspaces/{WS_ID}/projects"


@responses.activate
def test_list_tasks(backend):
    tasks = [make_task("t1", PROJ_ID, "Backend"), make_task("t2", PROJ_ID, "Frontend")]
    responses.add(
        responses.GET, TASKS_URL,
        json=tasks, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = backend.list_tasks(WS_ID, PROJ_ID)
    assert len(result) == 2
    assert result[0]["name"] == "Backend"


@responses.activate
def test_create_task(backend):
    task = make_task()
    responses.add(responses.POST, TASKS_URL, json=task, status=201)
    result = backend.create_task(WS_ID, PROJ_ID, {"name": "Backend", "status": "ACTIVE"})
    assert result["name"] == "Backend"


@responses.activate
def test_update_task(backend):
    task_id = "task111111111111111111111"
    updated = make_task(task_id, PROJ_ID, "Backend Updated", "DONE")
    responses.add(
        responses.PUT, f"{TASKS_URL}/{task_id}",
        json=updated, status=200,
    )
    result = backend.update_task(WS_ID, PROJ_ID, task_id, {"name": "Backend Updated", "status": "DONE"})
    assert result["status"] == "DONE"


@responses.activate
def test_delete_task(backend):
    task_id = "task111111111111111111111"
    responses.add(responses.DELETE, f"{TASKS_URL}/{task_id}", json={}, status=200)
    backend.delete_task(WS_ID, PROJ_ID, task_id)


@responses.activate
def test_tasks_list_name_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    # Mock the project lookup (--project is a name lookup)
    responses.add(
        responses.GET, PROJECTS_URL,
        json=[make_project(PROJ_ID, "Test Project")],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    responses.add(
        responses.GET, TASKS_URL,
        json=[make_task("t1", PROJ_ID, "Backend")],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "tasks", "list", "--project", PROJ_ID, "--name", "Backend", "--json"])
    assert result.exit_code == 0, result.output
    assert "name=Backend" in responses.calls[-1].request.url


@responses.activate
def test_tasks_list_is_active_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, PROJECTS_URL,
        json=[make_project(PROJ_ID, "Test Project")],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    responses.add(
        responses.GET, TASKS_URL,
        json=[make_task("t1", PROJ_ID, "Active Task")],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "tasks", "list", "--project", PROJ_ID, "--is-active", "--json"])
    assert result.exit_code == 0, result.output
    assert "is-active=true" in responses.calls[-1].request.url
