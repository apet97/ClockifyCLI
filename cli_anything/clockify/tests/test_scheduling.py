"""Tests for scheduling assignment operations."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import BASE_URL, WS_ID, API_KEY, make_assignment

SCHEDULING_URL = f"{BASE_URL}/workspaces/{WS_ID}/scheduling/assignments"


@responses.activate
def test_list_all_assignments(backend):
    """list_all_assignments returns all assignments."""
    assignments = [make_assignment("a1"), make_assignment("a2")]
    responses.add(
        responses.GET, f"{SCHEDULING_URL}/all",
        json=assignments, status=200,
        match_querystring=False,
    )
    result = backend.list_all_assignments(WS_ID)
    assert len(result) == 2


@responses.activate
def test_create_recurring_assignment(backend):
    """create_recurring_assignment POSTs to the recurring endpoint."""
    asgn = make_assignment()
    responses.add(
        responses.POST, f"{SCHEDULING_URL}/recurring",
        json=asgn, status=201,
    )
    result = backend.create_recurring_assignment(WS_ID, {
        "projectId": asgn["projectId"],
        "userId": asgn["userId"],
        "start": asgn["start"],
        "end": asgn["end"],
        "hoursPerDay": asgn["hoursPerDay"],
    })
    assert result["id"] == asgn["id"]


@responses.activate
def test_update_recurring_assignment(backend):
    """update_recurring_assignment PATCHes the assignment."""
    asgn = make_assignment()
    updated = dict(asgn)
    updated["hoursPerDay"] = 6.0
    url = f"{SCHEDULING_URL}/recurring/{asgn['id']}"
    responses.add(responses.PATCH, url, json=updated, status=200)
    result = backend.update_recurring_assignment(WS_ID, asgn["id"], {"hoursPerDay": 6.0})
    assert result["hoursPerDay"] == 6.0


@responses.activate
def test_delete_recurring_assignment(backend):
    """delete_recurring_assignment sends DELETE."""
    asgn_id = "asgn1111111111111111111111"
    url = f"{SCHEDULING_URL}/recurring/{asgn_id}"
    responses.add(responses.DELETE, url, json={}, status=200)
    result = backend.delete_recurring_assignment(WS_ID, asgn_id)
    assert isinstance(result, dict)
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_publish_assignments(backend):
    """publish_assignments PUTs to the publish endpoint."""
    responses.add(
        responses.PUT, f"{SCHEDULING_URL}/publish",
        json={"published": 3}, status=200,
    )
    result = backend.publish_assignments(WS_ID, {"week": "2026-W11"})
    assert result["published"] == 3


@responses.activate
def test_get_project_assignment_totals(backend):
    """get_project_assignment_totals GETs project totals."""
    project_id = "proj111111111111111111111111"
    url = f"{SCHEDULING_URL}/projects/totals/{project_id}"
    payload = {"totalHours": 40, "projectId": project_id}
    responses.add(responses.GET, url, json=payload, status=200)
    result = backend.get_project_assignment_totals(WS_ID, project_id)
    assert result["totalHours"] == 40
    assert result["projectId"] == project_id


@responses.activate
def test_get_user_capacity(backend):
    """get_user_capacity GETs user totals."""
    user_id = "user222222222222222222222222"
    url = f"{SCHEDULING_URL}/users/{user_id}/totals"
    payload = {"totalHours": 40, "userId": user_id}
    responses.add(responses.GET, url, json=payload, status=200)
    result = backend.get_user_capacity(WS_ID, user_id)
    assert result["totalHours"] == 40
    assert result["userId"] == user_id


@responses.activate
def test_assignments_list_sort_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, f"{SCHEDULING_URL}/all",
        json=[make_assignment()],
        status=200,
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "scheduling", "assignments", "list", "--start", "2024-01-01", "--end", "2024-12-31", "--sort-column", "USER", "--sort-order", "ASCENDING", "--json"])
    assert result.exit_code == 0, result.output
    assert "sort-column=USER" in responses.calls[0].request.url


@responses.activate
def test_assignments_list_name_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, f"{SCHEDULING_URL}/all",
        json=[make_assignment()],
        status=200,
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "scheduling", "assignments", "list", "--start", "2024-01-01", "--end", "2024-12-31", "--name", "Sprint", "--json"])
    assert result.exit_code == 0, result.output
    assert "name=Sprint" in responses.calls[0].request.url
