"""Tests covering OpenAPI parity gaps — body fields, query params, new commands.

This file covers all Tier 1 + Tier 2 gaps added in the parity pass:
- Body field additions (A1-A18)
- Query param additions (B1-B10)
- New commands (D1-D4)
"""

from __future__ import annotations

import json
import responses

from click.testing import CliRunner

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, USER_ID, API_KEY,
    make_time_entry, make_project, make_client, make_task, make_tag,
    make_webhook, make_group, make_expense, make_invoice,
    make_assignment,
)
from cli_anything.clockify.clockify_cli import main

# ── URL constants ──────────────────────────────────────────────────────

ENTRIES_URL = f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries"
PROJECTS_URL = f"{BASE_URL}/workspaces/{WS_ID}/projects"
CLIENTS_URL = f"{BASE_URL}/workspaces/{WS_ID}/clients"
TAGS_URL = f"{BASE_URL}/workspaces/{WS_ID}/tags"
TASKS_BASE = f"{BASE_URL}/workspaces/{WS_ID}/projects"
WEBHOOKS_URL = f"{BASE_URL}/workspaces/{WS_ID}/webhooks"
GROUPS_URL = f"{BASE_URL}/workspaces/{WS_ID}/user-groups"
EXPENSES_URL = f"{BASE_URL}/workspaces/{WS_ID}/expenses"
INVOICES_URL = f"{BASE_URL}/workspaces/{WS_ID}/invoices"
CUSTOM_FIELDS_URL = f"{BASE_URL}/workspaces/{WS_ID}/custom-fields"
SHARED_REPORTS_URL = f"{BASE_URL}/workspaces/{WS_ID}/shared-reports"
SCHEDULING_BASE = f"{BASE_URL}/workspaces/{WS_ID}/scheduling/assignments"
TIME_OFF_POLICIES_URL = f"{BASE_URL}/workspaces/{WS_ID}/time-off/policies"
USERS_URL = f"{BASE_URL}/workspaces/{WS_ID}/users"

PROJECT_ID = "proj111111111111111111111"
TASK_ID = "task111111111111111111111"
TAG_ID = "tag1111111111111111111111"
CLIENT_ID = "client11111111111111111111"
ENTRY_ID = "entry111111111111111111111"
WEBHOOK_ID = "hook111111111111111111111"
GROUP_ID = "grp1111111111111111111111"
EXPENSE_ID = "exp1111111111111111111111"
INVOICE_ID = "inv1111111111111111111111"
CF_ID = "cf11111111111111111111111"
REPORT_ID = "rep1111111111111111111111"
ASGN_ID = "asgn1111111111111111111111"
POLICY_ID = "pol1111111111111111111111"
CATEGORY_ID = "cat1111111111111111111111"
USER_ID2 = "user333333333333333333333"


def _invoke(runner, args):
    return runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID] + args)


# ── Helpers: mock /workspaces and /user ───────────────────────────────

def _add_user_mock():
    responses.add(
        responses.GET, f"{BASE_URL}/user",
        json={"id": USER_ID, "name": "Test", "email": "t@t.com",
              "defaultWorkspace": WS_ID},
        status=200,
    )


# ══════════════════════════════════════════════════════════════════════
# GAP A — Body field additions
# ══════════════════════════════════════════════════════════════════════

# ── A1: entries add --task --billable ─────────────────────────────────

@responses.activate
def test_entries_add_task_and_billable(runner):
    """entries add --task and --billable are sent in the request body."""
    _add_user_mock()
    entry = make_time_entry(entry_id=ENTRY_ID)
    responses.add(responses.POST, ENTRIES_URL, json=entry, status=201)

    result = _invoke(runner, [
        "entries", "add",
        "--start", "2026-03-13T09:00:00Z",
        "--end", "2026-03-13T10:00:00Z",
        "--task", TASK_ID,
        "--billable",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["taskId"] == TASK_ID
    assert sent["billable"] is True


@responses.activate
def test_entries_add_no_billable(runner):
    """entries add --no-billable sends billable=false."""
    _add_user_mock()
    entry = make_time_entry(entry_id=ENTRY_ID)
    responses.add(responses.POST, ENTRIES_URL, json=entry, status=201)

    result = _invoke(runner, [
        "entries", "add",
        "--start", "2026-03-13T09:00:00Z",
        "--end", "2026-03-13T10:00:00Z",
        "--no-billable",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["billable"] is False


# ── A2: entries update --tag --task --billable ─────────────────────────

@responses.activate
def test_entries_update_tag_task_billable(runner):
    """entries update --tag, --task, --billable sent in body."""
    existing = make_time_entry(entry_id=ENTRY_ID)
    responses.add(
        responses.GET,
        f"{BASE_URL}/workspaces/{WS_ID}/time-entries/{ENTRY_ID}",
        json=existing, status=200,
    )
    responses.add(
        responses.PUT,
        f"{BASE_URL}/workspaces/{WS_ID}/time-entries/{ENTRY_ID}",
        json=existing, status=200,
    )

    result = _invoke(runner, [
        "entries", "update", ENTRY_ID,
        "--tag", TAG_ID,
        "--task", TASK_ID,
        "--billable",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["tagIds"] == [TAG_ID]
    assert sent["taskId"] == TASK_ID
    assert sent["billable"] is True


# ── A3: projects create --billable --note ─────────────────────────────

@responses.activate
def test_projects_create_billable_note(runner):
    """projects create --billable --note sends correct body fields."""
    project = make_project(project_id=PROJECT_ID)
    responses.add(responses.POST, PROJECTS_URL, json=project, status=201)

    result = _invoke(runner, [
        "projects", "create", "Test Project",
        "--billable",
        "--note", "internal project",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["billable"] is True
    assert sent["note"] == "internal project"


@responses.activate
def test_projects_create_hourly_rate(runner):
    """projects create --hourly-rate sends hourlyRate nested object."""
    project = make_project(project_id=PROJECT_ID)
    responses.add(responses.POST, PROJECTS_URL, json=project, status=201)

    result = _invoke(runner, [
        "projects", "create", "Billable Project",
        "--hourly-rate", "75.0",
        "--currency", "EUR",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["hourlyRate"] == {"amount": 75.0, "currency": "EUR"}


# ── A4: projects update --billable --public --client --note ───────────

@responses.activate
def test_projects_update_billable_public_client_note(runner):
    """projects update adds billable, isPublic, clientId, note to body."""
    existing = make_project(project_id=PROJECT_ID)
    responses.add(
        responses.GET, f"{PROJECTS_URL}/{PROJECT_ID}",
        json=existing, status=200,
    )
    responses.add(
        responses.PUT, f"{PROJECTS_URL}/{PROJECT_ID}",
        json=existing, status=200,
    )

    result = _invoke(runner, [
        "projects", "update", PROJECT_ID,
        "--billable",
        "--public",
        "--client", CLIENT_ID,
        "--note", "updated note",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["billable"] is True
    assert sent["isPublic"] is True
    assert sent["clientId"] == CLIENT_ID
    assert sent["note"] == "updated note"


# ── A5: clients create --note --address --email --currency ────────────

@responses.activate
def test_clients_create_full_fields(runner):
    """clients create sends note, address, email."""
    client = make_client(client_id=CLIENT_ID)
    responses.add(responses.POST, CLIENTS_URL, json=client, status=201)

    result = _invoke(runner, [
        "clients", "create", "Acme Corp",
        "--note", "VIP client",
        "--address", "123 Main St",
        "--email", "billing@acme.com",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["name"] == "Acme Corp"
    assert sent["note"] == "VIP client"
    assert sent["address"] == "123 Main St"
    assert sent["email"] == "billing@acme.com"


# ── A6: clients update --archived ─────────────────────────────────────

@responses.activate
def test_clients_update_archived(runner):
    """clients update --archived sends archived=true."""
    client = make_client(client_id=CLIENT_ID)
    responses.add(
        responses.PUT, f"{CLIENTS_URL}/{CLIENT_ID}",
        json=client, status=200,
    )

    result = _invoke(runner, [
        "clients", "update", CLIENT_ID,
        "--name", "Acme",
        "--archived",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["name"] == "Acme"
    assert sent["archived"] is True


@responses.activate
def test_clients_update_active(runner):
    """clients update --active sends archived=false."""
    client = make_client(client_id=CLIENT_ID)
    responses.add(
        responses.PUT, f"{CLIENTS_URL}/{CLIENT_ID}",
        json=client, status=200,
    )

    result = _invoke(runner, [
        "clients", "update", CLIENT_ID,
        "--active",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["archived"] is False


# ── A7/A8: tasks create/update --assignee-id --estimate --billable ────

@responses.activate
def test_tasks_create_assignee_estimate_billable(runner):
    """tasks create sends assigneeIds, estimate, billable."""
    task = make_task(task_id=TASK_ID, project_id=PROJECT_ID)
    # _resolve_project_id does a list_projects(name=...) search for non-hex IDs
    responses.add(
        responses.GET, PROJECTS_URL,
        json=[make_project(project_id=PROJECT_ID)], status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    responses.add(
        responses.POST, f"{TASKS_BASE}/{PROJECT_ID}/tasks",
        json=task, status=201,
    )

    result = _invoke(runner, [
        "tasks", "create", "Implement feature",
        "--project", PROJECT_ID,
        "--assignee-id", USER_ID,
        "--assignee-id", USER_ID2,
        "--estimate", "PT8H",
        "--billable",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert set(sent["assigneeIds"]) == {USER_ID, USER_ID2}
    assert sent["estimate"] == "PT8H"
    assert sent["billable"] is True


@responses.activate
def test_tasks_update_assignee_estimate_billable(runner):
    """tasks update merges assigneeIds, estimate, billable into body."""
    existing = make_task(task_id=TASK_ID, project_id=PROJECT_ID)
    # _resolve_project_id does a list_projects(name=...) search for non-hex IDs
    responses.add(
        responses.GET, PROJECTS_URL,
        json=[make_project(project_id=PROJECT_ID)], status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    responses.add(
        responses.GET, f"{TASKS_BASE}/{PROJECT_ID}/tasks/{TASK_ID}",
        json=existing, status=200,
    )
    responses.add(
        responses.PUT, f"{TASKS_BASE}/{PROJECT_ID}/tasks/{TASK_ID}",
        json=existing, status=200,
    )

    result = _invoke(runner, [
        "tasks", "update", TASK_ID,
        "--project", PROJECT_ID,
        "--assignee-id", USER_ID,
        "--estimate", "PT4H",
        "--no-billable",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["assigneeIds"] == [USER_ID]
    assert sent["estimate"] == "PT4H"
    assert sent["billable"] is False


# ── A9: webhooks create --enabled --trigger-source --worker-url ───────

@responses.activate
def test_webhooks_create_extra_fields(runner):
    """webhooks create sends enabled, workerUrl, authorizationHeader, triggerSources."""
    hook = make_webhook(webhook_id=WEBHOOK_ID)
    responses.add(responses.POST, WEBHOOKS_URL, json=hook, status=201)

    result = _invoke(runner, [
        "webhooks", "create",
        "--url", "https://example.com/hook",
        "--name", "My Hook",
        "--event", "NEW_TIME_ENTRY",
        "--worker-url", "https://worker.example.com/hook",
        "--disabled",
        "--auth-header", "Bearer secret123",
        "--trigger-source", "proj111",
        "--trigger-source", "proj222",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["enabled"] is False
    assert sent["workerUrl"] == "https://worker.example.com/hook"
    assert sent["authorizationHeader"] == "Bearer secret123"
    assert set(sent["triggerSource"]) == {"proj111", "proj222"}


# ── A10: webhooks update --enabled --trigger ───────────────────────────

@responses.activate
def test_webhooks_update_enabled_trigger(runner):
    """webhooks update --enabled/--disabled and --trigger sent in body."""
    hook = make_webhook(webhook_id=WEBHOOK_ID)
    responses.add(
        responses.GET, f"{WEBHOOKS_URL}/{WEBHOOK_ID}",
        json=hook, status=200,
    )
    responses.add(
        responses.PUT, f"{WEBHOOKS_URL}/{WEBHOOK_ID}",
        json=hook, status=200,
    )

    result = _invoke(runner, [
        "webhooks", "update", WEBHOOK_ID,
        "--disabled",
        "--event", "TIMER_STOPPED",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["enabled"] is False
    assert sent["webhookEvent"] == "TIMER_STOPPED"


# ── A11: invoices create key fields ───────────────────────────────────

@responses.activate
def test_invoices_create_key_fields(runner):
    """invoices create sends name, dueDate, issueDate, currency, note."""
    invoice = make_invoice(invoice_id=INVOICE_ID)
    responses.add(responses.POST, INVOICES_URL, json=invoice, status=201)

    result = _invoke(runner, [
        "invoices", "create",
        "--name", "INV-2026-001",
        "--due-date", "2026-04-01",
        "--issue-date", "2026-03-13",
        "--currency", "EUR",
        "--note", "Net 30",
        "--tax", "21.0",
        "--discount", "5.0",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["number"] == "INV-2026-001"
    assert sent["dueDate"] == "2026-04-01"
    assert sent["issuedDate"] == "2026-03-13"
    assert sent["currency"] == "EUR"
    assert sent["note"] == "Net 30"
    assert sent["tax"] == 21.0
    assert sent["discount"] == 5.0


# ── A13: expenses create --billable --user-id --project-id --task-id ──

@responses.activate
def test_expenses_create_full_fields(runner):
    """expenses create sends userId, projectId, taskId, billable, quantity."""
    expense = make_expense(expense_id=EXPENSE_ID)
    responses.add(responses.POST, EXPENSES_URL, json=expense, status=201)

    result = _invoke(runner, [
        "expenses", "create",
        "--category-id", CATEGORY_ID,
        "--amount", "150.0",
        "--date", "2026-03-13",
        "--user-id", USER_ID2,
        "--project-id", PROJECT_ID,
        "--task-id", TASK_ID,
        "--billable",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["userId"] == USER_ID2
    assert sent["projectId"] == PROJECT_ID
    assert sent["taskId"] == TASK_ID
    assert sent["billable"] is True
    assert sent["amount"] == 150.0


# ── A14: expenses update full fields ──────────────────────────────────

@responses.activate
def test_expenses_update_full_fields(runner):
    """expenses update sends categoryId, date, quantity, userId, projectId, taskId, billable."""
    expense = make_expense(expense_id=EXPENSE_ID)
    responses.add(
        responses.PUT, f"{EXPENSES_URL}/{EXPENSE_ID}",
        json=expense, status=200,
    )

    result = _invoke(runner, [
        "expenses", "update", EXPENSE_ID,
        "--category-id", CATEGORY_ID,
        "--date", "2026-03-15",
        "--user-id", USER_ID2,
        "--project-id", PROJECT_ID,
        "--task-id", TASK_ID,
        "--billable",
        "--change-field", "DATE",
        "--change-field", "CATEGORY",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["categoryId"] == CATEGORY_ID
    assert sent["date"] == "2026-03-15T00:00:00Z"
    assert sent["userId"] == USER_ID2
    assert sent["projectId"] == PROJECT_ID
    assert sent["taskId"] == TASK_ID
    assert sent["billable"] is True
    assert sent["changeFields"] == ["DATE", "CATEGORY"]


# ── A15: scheduling assignments update-series ─────────────────────────

@responses.activate
def test_assignments_update_series_full_body(runner):
    """assignments update-series sends weeks and repeat per RecurringAssignmentRequestV1."""
    responses.add(
        responses.PUT,
        f"{SCHEDULING_BASE}/series/{ASGN_ID}",
        json={}, status=200,
    )

    result = _invoke(runner, [
        "scheduling", "assignments", "update-series", ASGN_ID,
        "--weeks", "4",
        "--repeat",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["weeks"] == 4
    assert sent["repeat"] is True


def test_assignments_update_series_invalid_option(runner):
    """assignments update-series --weeks is required."""
    result = _invoke(runner, [
        "scheduling", "assignments", "update-series", ASGN_ID,
        "--json",
    ])
    assert result.exit_code != 0


# ── A16: scheduling assignments publish ───────────────────────────────

@responses.activate
def test_assignments_publish_with_dates(runner):
    """assignments publish sends start and end in body."""
    responses.add(
        responses.PUT,
        f"{SCHEDULING_BASE}/publish",
        json={}, status=200,
    )

    result = _invoke(runner, [
        "scheduling", "assignments", "publish",
        "--start", "2026-04-01",
        "--end", "2026-04-30",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["start"] == "2026-04-01"
    assert sent["end"] == "2026-04-30"


# ── A17/A18: groups create/update --user-id ───────────────────────────

@responses.activate
def test_groups_create_with_user_ids(runner):
    """groups create --user-id sends userIds in body."""
    group = make_group(group_id=GROUP_ID)
    responses.add(responses.POST, GROUPS_URL, json=group, status=201)

    result = _invoke(runner, [
        "groups", "create", "Dev Team",
        "--user-id", USER_ID,
        "--user-id", USER_ID2,
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert set(sent["userIds"]) == {USER_ID, USER_ID2}


@responses.activate
def test_groups_update_with_user_ids(runner):
    """groups update --user-id sends userIds in body."""
    group = make_group(group_id=GROUP_ID)
    responses.add(
        responses.PUT, f"{GROUPS_URL}/{GROUP_ID}",
        json=group, status=200,
    )

    result = _invoke(runner, [
        "groups", "update", GROUP_ID,
        "--name", "Backend Team",
        "--user-id", USER_ID,
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["name"] == "Backend Team"
    assert sent["userIds"] == [USER_ID]


# ══════════════════════════════════════════════════════════════════════
# GAP B — Query param additions
# ══════════════════════════════════════════════════════════════════════

# ── B1: entries list ──────────────────────────────────────────────────

@responses.activate
def test_entries_list_hydrated(backend):
    """list_entries with hydrated=True sends hydrated=true query param."""
    entries = [make_time_entry()]
    responses.add(
        responses.GET, ENTRIES_URL,
        json=entries, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    backend.list_entries(WS_ID, USER_ID, hydrated=True)
    assert "hydrated=true" in responses.calls[0].request.url


@responses.activate
def test_entries_list_project_required(backend):
    """list_entries with project_required sends project-required param."""
    responses.add(
        responses.GET, ENTRIES_URL,
        json=[], status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    backend.list_entries(WS_ID, USER_ID, project_required=True)
    assert "project-required=true" in responses.calls[0].request.url


# ── B2: projects list ─────────────────────────────────────────────────

@responses.activate
def test_projects_list_new_params(backend):
    """list_projects sends strict-name-search, client-status, access."""
    responses.add(
        responses.GET, PROJECTS_URL,
        json=[], status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    backend.list_projects(
        WS_ID,
        strict_name_search=True,
        client_status="ACTIVE",
        access="PUBLIC",
        hydrated=True,
    )
    url = responses.calls[0].request.url
    assert "strict-name-search=true" in url
    assert "client-status=ACTIVE" in url
    assert "access=PUBLIC" in url
    assert "hydrated=true" in url


# ── B3: tasks list ────────────────────────────────────────────────────

@responses.activate
def test_tasks_list_sort_params(backend):
    """list_tasks sends sort-column and sort-order."""
    responses.add(
        responses.GET, f"{TASKS_BASE}/{PROJECT_ID}/tasks",
        json=[], status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    backend.list_tasks(WS_ID, PROJECT_ID, sort_column="NAME", sort_order="ASCENDING")
    url = responses.calls[0].request.url
    assert "sort-column=NAME" in url
    assert "sort-order=ASCENDING" in url


def test_tasks_list_invalid_sort_column(runner):
    """tasks list --sort-column INVALID fails validation."""
    result = _invoke(runner, [
        "tasks", "list", "--project", PROJECT_ID,
        "--sort-column", "INVALID",
    ])
    assert result.exit_code != 0


# ── B4: tags list ─────────────────────────────────────────────────────

@responses.activate
def test_tags_list_excluded_ids(backend):
    """list_tags sends excluded-ids param."""
    responses.add(
        responses.GET, TAGS_URL,
        json=[], status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    backend.list_tags(WS_ID, excluded_ids=[TAG_ID])
    assert "excluded-ids=" in responses.calls[0].request.url


# ── B5: clients list ──────────────────────────────────────────────────

@responses.activate
def test_clients_list_sort(backend):
    """list_clients sends sort-column and sort-order."""
    responses.add(
        responses.GET, CLIENTS_URL,
        json=[], status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    backend.list_clients(WS_ID, sort_column="NAME", sort_order="DESCENDING")
    url = responses.calls[0].request.url
    assert "sort-column=NAME" in url
    assert "sort-order=DESCENDING" in url


# ── B6: users list ────────────────────────────────────────────────────

@responses.activate
def test_users_list_new_params(backend):
    """list_users sends memberships, include-roles, sort-column."""
    responses.add(
        responses.GET, USERS_URL,
        json=[], status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    backend.list_users(
        WS_ID,
        memberships="ALL",
        include_roles=True,
        sort_column="NAME",
        sort_order="ASCENDING",
    )
    url = responses.calls[0].request.url
    assert "memberships=ALL" in url
    assert "include-roles=true" in url
    assert "sort-column=NAME" in url


def test_users_list_invalid_memberships(runner):
    """users list --memberships INVALID fails validation."""
    result = _invoke(runner, [
        "users", "list", "--memberships", "INVALID",
    ])
    assert result.exit_code != 0


def test_users_list_invalid_sort_column(runner):
    """users list --sort-column INVALID fails validation."""
    result = _invoke(runner, [
        "users", "list", "--sort-column", "INVALID",
    ])
    assert result.exit_code != 0


# ── B7: groups list ───────────────────────────────────────────────────

@responses.activate
def test_groups_list_sort_and_team_managers(backend):
    """list_groups sends sort-column, sort-order, includeTeamManagers."""
    responses.add(
        responses.GET, GROUPS_URL,
        json=[], status=200,
        match_querystring=False,
    )
    backend.list_groups(WS_ID, sort_column="NAME", sort_order="ASCENDING", include_team_managers=True)
    url = responses.calls[0].request.url
    assert "sort-column=NAME" in url
    assert "includeTeamManagers=true" in url


# ── B9/B10: expense categories list and custom-fields list ────────────

@responses.activate
def test_expense_categories_list_params(backend):
    """list_expense_categories sends name, archived, sort-column."""
    responses.add(
        responses.GET, f"{EXPENSES_URL}/categories",
        json=[], status=200,
        match_querystring=False,
    )
    backend.list_expense_categories(WS_ID, name="Travel", sort_column="NAME", sort_order="ASCENDING")
    url = responses.calls[0].request.url
    assert "name=Travel" in url
    assert "sort-column=NAME" in url


@responses.activate
def test_custom_fields_list_params(backend):
    """list_custom_fields sends name, status, entity-type."""
    responses.add(
        responses.GET, CUSTOM_FIELDS_URL,
        json=[], status=200,
        match_querystring=False,
    )
    backend.list_custom_fields(WS_ID, name="Ticket", status="ACTIVE", entity_types=["TIME_ENTRY"])
    url = responses.calls[0].request.url
    assert "name=Ticket" in url
    assert "status=ACTIVE" in url
    assert "entity-type=" in url


def test_custom_fields_list_invalid_status(runner):
    """custom-fields list --status INVALID fails validation."""
    result = _invoke(runner, [
        "custom-fields", "list", "--status", "INVALID",
    ])
    assert result.exit_code != 0


def test_custom_fields_list_invalid_entity_type(runner):
    """custom-fields list --entity-type INVALID fails validation."""
    result = _invoke(runner, [
        "custom-fields", "list", "--entity-type", "INVALID",
    ])
    assert result.exit_code != 0


# ══════════════════════════════════════════════════════════════════════
# GAP D — New commands
# ══════════════════════════════════════════════════════════════════════

# ── D1: shared-reports get ────────────────────────────────────────────

@responses.activate
def test_shared_reports_get(runner):
    """shared-reports get <id> returns report JSON."""
    report = {"id": REPORT_ID, "name": "Q1 Report", "workspaceId": WS_ID}
    responses.add(
        responses.GET, f"{SHARED_REPORTS_URL}/{REPORT_ID}",
        json=report, status=200,
    )
    result = _invoke(runner, [
        "shared-reports", "get", REPORT_ID, "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["id"] == REPORT_ID


# ── D2: custom-fields project edit ────────────────────────────────────

@responses.activate
def test_custom_fields_project_edit(runner):
    """custom-fields project edit sends value to PATCH endpoint."""
    cf = {"id": CF_ID, "name": "Ticket #", "defaultValue": "TKT-123"}
    responses.add(
        responses.PATCH,
        f"{PROJECTS_URL}/{PROJECT_ID}/custom-fields/{CF_ID}",
        json=cf, status=200,
    )
    result = _invoke(runner, [
        "custom-fields", "project", "edit", PROJECT_ID, CF_ID,
        "--value", "TKT-456",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["defaultValue"] == "TKT-456"


# ── D3: expenses categories archive ───────────────────────────────────

@responses.activate
def test_expense_categories_archive_command(runner):
    """expenses categories archive sends PATCH to status endpoint."""
    cat = {"id": CATEGORY_ID, "name": "Travel", "archived": True}
    responses.add(
        responses.PATCH,
        f"{EXPENSES_URL}/categories/{CATEGORY_ID}/status",
        json=cat, status=200,
    )
    result = _invoke(runner, [
        "expenses", "categories", "archive", CATEGORY_ID,
        "--archived", "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["archived"] is True


@responses.activate
def test_expense_categories_activate_command(runner):
    """expenses categories archive --active sends archived=false."""
    cat = {"id": CATEGORY_ID, "name": "Travel", "archived": False}
    responses.add(
        responses.PATCH,
        f"{EXPENSES_URL}/categories/{CATEGORY_ID}/status",
        json=cat, status=200,
    )
    result = _invoke(runner, [
        "expenses", "categories", "archive", CATEGORY_ID,
        "--active", "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["archived"] is False


# ── D4: time-off policies status ──────────────────────────────────────

@responses.activate
def test_time_off_policies_status_command(runner):
    """time-off policies status sends PATCH to policies/{id} endpoint."""
    policy = {"id": POLICY_ID, "name": "Annual Leave", "status": "ARCHIVED"}
    responses.add(
        responses.PATCH,
        f"{TIME_OFF_POLICIES_URL}/{POLICY_ID}",
        json=policy, status=200,
    )
    result = _invoke(runner, [
        "time-off", "policies", "status", POLICY_ID,
        "--status", "ARCHIVED",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["status"] == "ARCHIVED"


def test_time_off_policies_status_invalid(runner):
    """time-off policies status --status INVALID fails validation."""
    result = _invoke(runner, [
        "time-off", "policies", "status", POLICY_ID,
        "--status", "INVALID",
    ])
    assert result.exit_code != 0


# ══════════════════════════════════════════════════════════════════════
# GAP C — Enum constraints
# ══════════════════════════════════════════════════════════════════════

def test_assignments_update_series_weeks_required(runner):
    """scheduling update-series --weeks is required."""
    result = _invoke(runner, [
        "scheduling", "assignments", "update-series", ASGN_ID,
        "--json",
    ])
    assert result.exit_code != 0


def test_projects_list_access_choices(runner):
    """projects list --access only accepts PUBLIC or PRIVATE."""
    result = _invoke(runner, [
        "projects", "list", "--access", "INVALID",
    ])
    assert result.exit_code != 0


def test_projects_list_client_status_choices(runner):
    """projects list --client-status only accepts ACTIVE/ARCHIVED/ALL."""
    result = _invoke(runner, [
        "projects", "list", "--client-status", "INVALID",
    ])
    assert result.exit_code != 0


# ── Iteration 6/7: extra-body and new parameter tests ────────────────


REPORTS_URL = "https://reports.api.clockify.me/v1"
USER_URL = f"{BASE_URL}/user"


def _add_user_mock():
    """Register mock for /user endpoint (needed for _user(ctx) resolution)."""
    responses.add(
        responses.GET, USER_URL,
        json={"id": USER_ID, "defaultWorkspace": WS_ID},
        status=200,
    )


@responses.activate
def test_extra_body_merges_into_request(runner):
    """--extra-body deep-merges JSON into the request body."""
    _add_user_mock()
    responses.add(
        responses.POST, f"{ENTRIES_URL}",
        json=make_time_entry(), status=201,
    )
    extra = json.dumps({"customFields": [{"customFieldId": "cf1", "value": "test"}]})
    result = _invoke(runner, [
        "--extra-body", extra,
        "entries", "add",
        "--start", "2026-03-14T09:00:00Z", "--end", "2026-03-14T17:00:00Z",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["customFields"] == [{"customFieldId": "cf1", "value": "test"}]
    assert "start" in sent


@responses.activate
def test_extra_body_deep_merges_nested(runner):
    """--extra-body deep-merges nested structures without overwriting existing keys."""
    responses.add(
        responses.POST, f"{REPORTS_URL}/workspaces/{WS_ID}/reports/summary",
        json={"totals": []}, status=200,
    )
    extra = json.dumps({"users": {"contains": "DOES_NOT_CONTAIN", "status": "ACTIVE"}})
    result = _invoke(runner, [
        "--extra-body", extra,
        "reports", "summary", "--start", "2026-03-01", "--end", "2026-03-14",
        "--user", USER_ID, "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    # The --user option sets ids and contains=CONTAINS, but --extra-body should override
    assert sent["users"]["contains"] == "DOES_NOT_CONTAIN"
    assert sent["users"]["status"] == "ACTIVE"
    assert sent["users"]["ids"] == [USER_ID]


@responses.activate
def test_timer_start_billable_and_type(runner):
    """timer start passes --billable and --type to body."""
    _add_user_mock()
    responses.add(
        responses.POST, f"{ENTRIES_URL}",
        json=make_time_entry(), status=201,
    )
    result = _invoke(runner, [
        "timer", "start", "--billable", "--type", "BREAK", "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["billable"] is True
    assert sent["type"] == "BREAK"


@responses.activate
def test_users_make_manager_body(runner):
    """users make-manager sends role, entityId, sourceType in body."""
    responses.add(
        responses.POST, f"{USERS_URL}/{USER_ID}/roles",
        json={}, status=200,
    )
    result = _invoke(runner, [
        "users", "make-manager", USER_ID,
        "--role", "TEAM_MANAGER", "--entity-id", "ws123", "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["role"] == "TEAM_MANAGER"
    assert sent["entityId"] == "ws123"


@responses.activate
def test_report_summary_tag_filter(runner):
    """reports summary passes --tag to body as tags filter."""
    responses.add(
        responses.POST, f"{REPORTS_URL}/workspaces/{WS_ID}/reports/summary",
        json={"totals": []}, status=200,
    )
    result = _invoke(runner, [
        "reports", "summary", "--start", "2026-03-01", "--end", "2026-03-14",
        "--tag", TAG_ID, "--description", "test desc", "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["tags"] == {"ids": [TAG_ID], "contains": "CONTAINS"}
    assert sent["description"] == "test desc"


@responses.activate
def test_report_weekly_client_and_tag(runner):
    """reports weekly passes --client and --tag to body."""
    responses.add(
        responses.POST, f"{REPORTS_URL}/workspaces/{WS_ID}/reports/weekly",
        json={"weeklyTotals": []}, status=200,
    )
    result = _invoke(runner, [
        "reports", "weekly", "--start", "2026-03-01", "--end", "2026-03-14",
        "--client", CLIENT_ID, "--tag", TAG_ID, "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["clients"] == {"ids": [CLIENT_ID], "contains": "CONTAINS"}
    assert sent["tags"] == {"ids": [TAG_ID], "contains": "CONTAINS"}


@responses.activate
def test_webhook_logs_filter(runner):
    """webhooks logs passes filter body fields."""
    responses.add(
        responses.POST, f"{WEBHOOKS_URL}/{WEBHOOK_ID}/logs",
        json={"logs": []}, status=200,
    )
    result = _invoke(runner, [
        "webhooks", "logs", WEBHOOK_ID,
        "--from", "2026-03-01T00:00:00Z", "--status", "FAILED", "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["from"] == "2026-03-01T00:00:00Z"
    assert sent["status"] == "FAILED"


@responses.activate
def test_custom_fields_update_type(runner):
    """custom-fields update passes --field-type to body."""
    responses.add(
        responses.PUT, f"{CUSTOM_FIELDS_URL}/{CF_ID}",
        json={"id": CF_ID, "type": "NUMBER"}, status=200,
    )
    result = _invoke(runner, [
        "custom-fields", "update", CF_ID,
        "--field-type", "NUMBER", "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["type"] == "NUMBER"


@responses.activate
def test_invoices_filter_issue_date_range(runner):
    """invoices filter passes --issue-date-start/end to body."""
    responses.add(
        responses.POST, f"{INVOICES_URL}/info",
        json=[], status=200,
    )
    result = _invoke(runner, [
        "invoices", "filter",
        "--issue-date-start", "2026-01-01", "--issue-date-end", "2026-03-31",
        "--company", "comp123", "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["issueDate"]["start"] == "2026-01-01T00:00:00Z"
    assert sent["issueDate"]["end"] == "2026-03-31T23:59:59Z"
    assert sent["companies"] == {"ids": ["comp123"]}


# ══════════════════════════════════════════════════════════════════════
# Final parity fixes — spec compliance
# ══════════════════════════════════════════════════════════════════════

HOLIDAYS_URL = f"{BASE_URL}/workspaces/{WS_ID}/holidays"
from cli_anything.clockify.tests.conftest import make_holiday, make_custom_field


@responses.activate
def test_webhook_logs_pagination(runner):
    """webhooks logs --page and --page-size pass query params."""
    responses.add(
        responses.POST, f"{WEBHOOKS_URL}/{WEBHOOK_ID}/logs",
        json={"logs": []}, status=200,
    )
    result = _invoke(runner, [
        "webhooks", "logs", WEBHOOK_ID,
        "--page", "2", "--page-size", "10", "--json",
    ])
    assert result.exit_code == 0, result.output
    url = responses.calls[0].request.url
    assert "page=2" in url
    assert "page-size=10" in url


@responses.activate
def test_holidays_in_period_date_format(runner):
    """holidays in-period sends dates without T00:00:00Z suffix."""
    responses.add(
        responses.GET, f"{HOLIDAYS_URL}/in-period",
        json=[make_holiday()], status=200,
        match_querystring=False,
    )
    result = _invoke(runner, [
        "holidays", "in-period",
        "--start", "2026-01-01", "--end", "2026-12-31",
        "--assigned-to", USER_ID, "--json",
    ])
    assert result.exit_code == 0, result.output
    url = responses.calls[0].request.url
    assert "T00%3A00%3A00Z" not in url
    assert "T23%3A59%3A59Z" not in url
    assert "start=2026-01-01" in url
    assert "end=2026-12-31" in url


@responses.activate
def test_custom_fields_project_list_filters(runner):
    """custom-fields project list --status sends query param."""
    responses.add(
        responses.GET,
        f"{PROJECTS_URL}/{PROJECT_ID}/custom-fields",
        json=[make_custom_field()], status=200,
        match_querystring=False,
    )
    result = _invoke(runner, [
        "custom-fields", "project", "list", PROJECT_ID,
        "--status", "VISIBLE", "--json",
    ])
    assert result.exit_code == 0, result.output
    assert "status=VISIBLE" in responses.calls[0].request.url


@responses.activate
def test_bulk_update_sends_array(runner):
    """entries bulk-update sends body as array with per-entry objects."""
    _add_user_mock()
    entries_url = f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries"
    responses.add(responses.PUT, entries_url, json={"updated": 2}, status=200)
    result = _invoke(runner, [
        "entries", "bulk-update",
        "--ids", "e1111111111111111111111111",
        "--ids", "e2222222222222222222222222",
        "--description", "Bulk test",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    put_call = next(c for c in responses.calls if c.request.method == "PUT")
    body = json.loads(put_call.request.body)
    assert isinstance(body, list), "Body must be an array per spec"
    assert len(body) == 2
    for item in body:
        assert "id" in item
        assert item["description"] == "Bulk test"


# ══════════════════════════════════════════════════════════════════════
# Phase 1A — entries add-direct (workspace-scoped, no user ID)
# ══════════════════════════════════════════════════════════════════════

@responses.activate
def test_entries_add_direct(runner):
    """entries add-direct POSTs to workspace-scoped endpoint."""
    entry = make_time_entry()
    responses.add(
        responses.POST,
        f"{BASE_URL}/workspaces/{WS_ID}/time-entries",
        json=entry, status=201,
    )
    result = runner.invoke(main, [
        "--api-key", API_KEY,
        "--workspace", WS_ID,
        "entries", "add-direct",
        "--start", "2026-03-13T09:00:00Z",
        "--end", "2026-03-13T10:00:00Z",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert "start" in body


# ══════════════════════════════════════════════════════════════════════
# Phase 1B — time-off policies update missing fields
# ══════════════════════════════════════════════════════════════════════

@responses.activate
def test_time_off_policies_update_approve_users(runner):
    """time-off policies update sends approve, users, userGroups in body."""
    POLICY_ID = "pol1111111111111111111111"
    responses.add(
        responses.PUT,
        f"{BASE_URL}/workspaces/{WS_ID}/time-off/policies/{POLICY_ID}",
        json={"id": POLICY_ID}, status=200,
    )
    result = runner.invoke(main, [
        "--api-key", API_KEY,
        "--workspace", WS_ID,
        "time-off", "policies", "update", POLICY_ID,
        "--approve", '{"type":"MANAGER"}',
        "--user", "uid1111111111111111111111",
        "--user-group", "gid1111111111111111111111",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["approve"] == {"type": "MANAGER"}
    assert body["users"] == ["uid1111111111111111111111"]
    assert body["userGroups"] == ["gid1111111111111111111111"]


# ══════════════════════════════════════════════════════════════════════
# Phase 1C — shared-reports get-public (reports domain)
# ══════════════════════════════════════════════════════════════════════

@responses.activate
def test_shared_reports_get_public(runner):
    """shared-reports get-public GETs from reports domain."""
    RPT_ID = "rpt1111111111111111111111"
    responses.add(
        responses.GET,
        f"{REPORTS_URL}/shared-reports/{RPT_ID}",
        json={"id": RPT_ID, "name": "Public Report"},
        status=200,
        match_querystring=False,
    )
    result = runner.invoke(main, [
        "--api-key", API_KEY,
        "--workspace", WS_ID,
        "shared-reports", "get-public", RPT_ID, "--json",
    ])
    assert result.exit_code == 0, result.output
