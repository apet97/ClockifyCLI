"""Tests for 21 CLI commands that had no test coverage."""

from __future__ import annotations

import json
import os
import tempfile

import responses

from click.testing import CliRunner

from cli_anything.clockify.tests.conftest import (
    BASE_URL, REPORTS_URL, WS_ID, USER_ID, API_KEY,
    make_workspace, make_user, make_time_entry, make_assignment,
)
from cli_anything.clockify.clockify_cli import main

PROJECT_ID = "aabb11111111111111111111"  # 24-char hex to bypass name resolution
TASK_ID = "task111111111111111111111"
ENTRY_ID = "entry111111111111111111111"
CATEGORY_ID = "cat1111111111111111111111"
ASSIGNMENT_ID = "asgn1111111111111111111111"
FIELD_ID = "cf11111111111111111111111"
ENTITY_ID = "ent1111111111111111111111"


def _runner():
    return CliRunner()


def _base_args():
    return ["--api-key", API_KEY, "--workspace", WS_ID]


def _add_user_mock():
    """Add the GET /user mock needed for commands that resolve user ID."""
    responses.add(
        responses.GET,
        f"{BASE_URL}/user",
        json=make_user(),
        status=200,
        match_querystring=False,
    )


# ── 1. workspaces get ─────────────────────────────────────────────────

@responses.activate
def test_workspaces_get():
    """workspaces get <id> returns workspace JSON."""
    ws = make_workspace()
    responses.add(
        responses.GET,
        f"{BASE_URL}/workspaces/{WS_ID}",
        json=ws, status=200,
        match_querystring=False,
    )
    result = _runner().invoke(main, [*_base_args(), "workspaces", "get", WS_ID, "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["id"] == WS_ID


# ── 2. workspaces create ──────────────────────────────────────────────

@responses.activate
def test_workspaces_create():
    """workspaces create POSTs body with 'name'."""
    ws = make_workspace(name="New WS")
    responses.add(responses.POST, f"{BASE_URL}/workspaces", json=ws, status=201)
    result = _runner().invoke(main, [*_base_args(), "workspaces", "create", "New WS", "--json"])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["name"] == "New WS"


# ── 3. workspaces invite ──────────────────────────────────────────────

@responses.activate
def test_workspaces_invite():
    """workspaces invite POSTs email and passes send-email query param."""
    responses.add(
        responses.POST,
        f"{BASE_URL}/workspaces/{WS_ID}/users",
        json=make_user(email="new@example.com"),
        status=201,
        match_querystring=False,
    )
    result = _runner().invoke(main, [
        *_base_args(), "workspaces", "invite",
        "--email", "new@example.com", "--send-email", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["email"] == "new@example.com"
    assert "send-email" in responses.calls[0].request.url


# ── 4. tasks cost-rate ────────────────────────────────────────────────

@responses.activate
def test_tasks_cost_rate():
    """tasks cost-rate PUTs body with 'amount'."""
    responses.add(
        responses.PUT,
        f"{BASE_URL}/workspaces/{WS_ID}/projects/{PROJECT_ID}/tasks/{TASK_ID}/cost-rate",
        json={"amount": 5000}, status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "tasks", "cost-rate", TASK_ID,
        "--project", PROJECT_ID, "--amount", "5000", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["amount"] == 5000


# ── 5. tasks hourly-rate ──────────────────────────────────────────────

@responses.activate
def test_tasks_hourly_rate():
    """tasks hourly-rate PUTs body with 'amount'."""
    responses.add(
        responses.PUT,
        f"{BASE_URL}/workspaces/{WS_ID}/projects/{PROJECT_ID}/tasks/{TASK_ID}/hourly-rate",
        json={"amount": 7500}, status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "tasks", "hourly-rate", TASK_ID,
        "--project", PROJECT_ID, "--amount", "7500", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["amount"] == 7500


# ── 6. entries mark-invoiced ──────────────────────────────────────────

@responses.activate
def test_entries_mark_invoiced():
    """entries mark-invoiced PATCHes body with 'timeEntryIds'."""
    responses.add(
        responses.PATCH,
        f"{BASE_URL}/workspaces/{WS_ID}/time-entries/invoiced",
        json={}, status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "entries", "mark-invoiced",
        "--ids", f"{ENTRY_ID},entry222222222222222222222",
        "--invoiced", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert "timeEntryIds" in body
    assert len(body["timeEntryIds"]) == 2


# ── 7. entries duplicate ──────────────────────────────────────────────

@responses.activate
def test_entries_duplicate():
    """entries duplicate POSTs to .../duplicate."""
    _add_user_mock()
    entry = make_time_entry(entry_id="entry_dup_1111111111111111")
    responses.add(
        responses.POST,
        f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries/{ENTRY_ID}/duplicate",
        json=entry, status=201,
    )
    result = _runner().invoke(main, [*_base_args(), "entries", "duplicate", ENTRY_ID, "--json"])
    assert result.exit_code == 0, result.output


# ── 8. users upload-photo ─────────────────────────────────────────────

@responses.activate
def test_users_upload_photo():
    """users upload-photo POSTs multipart to /file/image."""
    responses.add(
        responses.POST,
        f"{BASE_URL}/file/image",
        json={"id": "photo123", "url": "https://img.clockify.me/photo.jpg"},
        status=200,
    )
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(b"\xff\xd8\xff\xe0fake-jpeg-data")
        tmp_path = f.name
    try:
        result = _runner().invoke(main, [
            *_base_args(), "users", "upload-photo", tmp_path, "--json",
        ])
        assert result.exit_code == 0, result.output
        assert len(responses.calls) >= 1
        assert "/file/image" in responses.calls[0].request.url
    finally:
        os.unlink(tmp_path)


# ── 9. users update-profile ──────────────────────────────────────────

@responses.activate
def test_users_update_profile():
    """users update-profile PATCHes body with profile fields."""
    responses.add(
        responses.PATCH,
        f"{BASE_URL}/workspaces/{WS_ID}/member-profile/{USER_ID}",
        json={"id": USER_ID, "name": "New Name"},
        status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "users", "update-profile", USER_ID,
        "--name", "New Name", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["name"] == "New Name"


# ── 10. users managers ────────────────────────────────────────────────

@responses.activate
def test_users_managers():
    """users managers GETs and returns list."""
    managers = [make_user(user_id="mgr1111111111111111111111", name="Manager 1")]
    responses.add(
        responses.GET,
        f"{BASE_URL}/workspaces/{WS_ID}/users/{USER_ID}/managers",
        json=managers, status=200,
        match_querystring=False,
    )
    result = _runner().invoke(main, [
        *_base_args(), "users", "managers", USER_ID, "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["id"] == "mgr1111111111111111111111"


# ── 11. users remove-manager ─────────────────────────────────────────

@responses.activate
def test_users_remove_manager():
    """users remove-manager DELETEs with role body."""
    responses.add(
        responses.DELETE,
        f"{BASE_URL}/workspaces/{WS_ID}/users/{USER_ID}/roles",
        json={}, status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "users", "remove-manager", USER_ID,
        "--role", "TEAM_MANAGER",
        "--entity-id", ENTITY_ID,
        "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["role"] == "TEAM_MANAGER"
    assert body["entityId"] == ENTITY_ID


# ── 12. users set-field ──────────────────────────────────────────────

@responses.activate
def test_users_set_field():
    """users set-field PUTs body with 'value'."""
    responses.add(
        responses.PUT,
        f"{BASE_URL}/workspaces/{WS_ID}/users/{USER_ID}/custom-field/{FIELD_ID}/value",
        json={"value": "PROJ-123"}, status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "users", "set-field", USER_ID, FIELD_ID,
        "--value", "PROJ-123", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["value"] == "PROJ-123"


# ── 13. projects template ────────────────────────────────────────────

@responses.activate
def test_projects_template():
    """projects template PATCHes body with 'isTemplate'."""
    responses.add(
        responses.PATCH,
        f"{BASE_URL}/workspaces/{WS_ID}/projects/{PROJECT_ID}/template",
        json={"id": PROJECT_ID, "isTemplate": True}, status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "projects", "template", PROJECT_ID,
        "--is-template", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["isTemplate"] is True


# ── 14. projects estimate ────────────────────────────────────────────

@responses.activate
def test_projects_estimate():
    """projects estimate PATCHes body with time estimate fields."""
    responses.add(
        responses.PATCH,
        f"{BASE_URL}/workspaces/{WS_ID}/projects/{PROJECT_ID}/estimate",
        json={"id": PROJECT_ID}, status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "projects", "estimate", PROJECT_ID,
        "--time-type", "MANUAL",
        "--time-estimate", "PT8H",
        "--time-active",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert "timeEstimate" in body
    assert body["timeEstimate"]["type"] == "MANUAL"
    assert body["timeEstimate"]["estimate"] == "PT8H"
    assert body["timeEstimate"]["active"] is True


# ── 15. projects members ─────────────────────────────────────────────

@responses.activate
def test_projects_members():
    """projects members PATCHes body with 'memberships'."""
    responses.add(
        responses.PATCH,
        f"{BASE_URL}/workspaces/{WS_ID}/projects/{PROJECT_ID}/memberships",
        json={"id": PROJECT_ID}, status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "projects", "members", PROJECT_ID,
        "--user-id", USER_ID,
        "--hourly-rate", "5000",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert "memberships" in body
    assert body["memberships"][0]["userId"] == USER_ID


# ── 16. reports attendance ────────────────────────────────────────────

@responses.activate
def test_reports_attendance():
    """reports attendance POSTs body with dateRangeStart/End."""
    responses.add(
        responses.POST,
        f"{REPORTS_URL}/workspaces/{WS_ID}/reports/attendance",
        json={"totals": [], "groupOne": []},
        status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "reports", "attendance",
        "--start", "2026-03-01",
        "--end", "2026-03-13",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert "dateRangeStart" in body
    assert "dateRangeEnd" in body


# ── 17. assignments copy ─────────────────────────────────────────────

@responses.activate
def test_assignments_copy():
    """assignments copy POSTs to .../copy."""
    responses.add(
        responses.POST,
        f"{BASE_URL}/workspaces/{WS_ID}/scheduling/assignments/{ASSIGNMENT_ID}/copy",
        json=make_assignment(), status=201,
    )
    result = _runner().invoke(main, [
        *_base_args(), "scheduling", "assignments", "copy", ASSIGNMENT_ID,
        "--user-id", USER_ID, "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["userId"] == USER_ID


# ── 18. expense categories create ────────────────────────────────────

@responses.activate
def test_expense_categories_create():
    """expense categories create POSTs body with 'name'."""
    responses.add(
        responses.POST,
        f"{BASE_URL}/workspaces/{WS_ID}/expenses/categories",
        json={"id": CATEGORY_ID, "name": "Travel"},
        status=201,
    )
    result = _runner().invoke(main, [
        *_base_args(), "expenses", "categories", "create", "Travel", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["name"] == "Travel"


# ── 19. expense categories delete ────────────────────────────────────

@responses.activate
def test_expense_categories_delete():
    """expense categories delete sends DELETE call."""
    responses.add(
        responses.DELETE,
        f"{BASE_URL}/workspaces/{WS_ID}/expenses/categories/{CATEGORY_ID}",
        json={}, status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "expenses", "categories", "delete", CATEGORY_ID,
        "--confirm", "--json",
    ])
    assert result.exit_code == 0, result.output
    assert len(responses.calls) >= 1
    assert responses.calls[0].request.method == "DELETE"


# ── 20. expense categories update ────────────────────────────────────

@responses.activate
def test_expense_categories_update():
    """expense categories update PUTs body with 'name'."""
    responses.add(
        responses.PUT,
        f"{BASE_URL}/workspaces/{WS_ID}/expenses/categories/{CATEGORY_ID}",
        json={"id": CATEGORY_ID, "name": "Meals"},
        status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "expenses", "categories", "update", CATEGORY_ID,
        "--name", "Meals", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["name"] == "Meals"


# ── 21. users update-status ──────────────────────────────────────────

@responses.activate
def test_users_update_status():
    """users update-status PUTs body with 'status'."""
    responses.add(
        responses.PUT,
        f"{BASE_URL}/workspaces/{WS_ID}/users/{USER_ID}",
        json={"id": USER_ID, "status": "INACTIVE"},
        status=200,
    )
    result = _runner().invoke(main, [
        *_base_args(), "users", "update-status", USER_ID,
        "--status", "INACTIVE", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["status"] == "INACTIVE"
