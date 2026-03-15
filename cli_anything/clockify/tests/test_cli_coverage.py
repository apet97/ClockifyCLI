"""Tests for 26 CLI commands added to reach 154/154 API endpoint coverage."""

from __future__ import annotations

import json
import responses

from click.testing import CliRunner

from cli_anything.clockify.tests.conftest import BASE_URL, WS_ID, API_KEY, USER_ID
from cli_anything.clockify.clockify_cli import main

# ── URL constants ──────────────────────────────────────────────────────

WS_URL = f"{BASE_URL}/workspaces/{WS_ID}"
PROJECTS_URL = f"{WS_URL}/projects"
USERS_URL = f"{WS_URL}/users"
WEBHOOKS_URL = f"{WS_URL}/webhooks"
EXPENSES_URL = f"{WS_URL}/expenses"
INVOICES_URL = f"{WS_URL}/invoices"
TIME_OFF_URL = f"{WS_URL}/time-off"
SCHEDULING_URL = f"{WS_URL}/scheduling/assignments"
APPROVAL_URL = f"{WS_URL}/approval-requests"

# ── ID constants ───────────────────────────────────────────────────────

PROJECT_ID = "proj111111111111111111111"
WEBHOOK_ID = "hook111111111111111111111"
ADDON_ID = "addon11111111111111111111"
EXPENSE_ID = "exp1111111111111111111111"
FILE_ID = "file111111111111111111111"
CATEGORY_ID = "cat1111111111111111111111"
INVOICE_ID = "inv1111111111111111111111"
POLICY_ID = "pol1111111111111111111111"
REQUEST_ID = "req1111111111111111111111"
ENTRY_ID = "entry111111111111111111111"


def _invoke(runner: CliRunner, args: list) -> object:
    return runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID] + args)


# ── 1.1 Workspace Rates ────────────────────────────────────────────────

@responses.activate
def test_workspaces_cost_rate(runner):
    """workspaces cost-rate updates workspace cost rate."""
    responses.add(responses.PUT, f"{WS_URL}/cost-rate", json={"amount": 10000}, status=200)
    result = _invoke(runner, ["workspaces", "cost-rate", "--amount", "10000", "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["amount"] == 10000


@responses.activate
def test_workspaces_hourly_rate(runner):
    """workspaces hourly-rate updates workspace hourly rate."""
    responses.add(responses.PUT, f"{WS_URL}/hourly-rate", json={"amount": 7500}, status=200)
    result = _invoke(runner, ["workspaces", "hourly-rate", "--amount", "7500", "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["amount"] == 7500


# ── 1.2 Project Membership & User Rates ───────────────────────────────

@responses.activate
def test_projects_add_members(runner):
    """projects add-members adds users to a project."""
    responses.add(
        responses.POST, f"{PROJECTS_URL}/{PROJECT_ID}/memberships",
        json={"id": PROJECT_ID, "memberships": []}, status=200,
    )
    result = _invoke(runner, [
        "projects", "add-members", PROJECT_ID,
        "--user-id", USER_ID, "--json",
    ])
    assert result.exit_code == 0, result.output


@responses.activate
def test_projects_user_cost_rate(runner):
    """projects user-cost-rate sets per-user cost rate on a project."""
    responses.add(
        responses.PUT,
        f"{PROJECTS_URL}/{PROJECT_ID}/users/{USER_ID}/cost-rate",
        json={"amount": 5000}, status=200,
    )
    result = _invoke(runner, [
        "projects", "user-cost-rate", PROJECT_ID, USER_ID,
        "--amount", "5000", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["amount"] == 5000


@responses.activate
def test_projects_user_hourly_rate(runner):
    """projects user-hourly-rate sets per-user hourly rate on a project."""
    responses.add(
        responses.PUT,
        f"{PROJECTS_URL}/{PROJECT_ID}/users/{USER_ID}/hourly-rate",
        json={"amount": 6000}, status=200,
    )
    result = _invoke(runner, [
        "projects", "user-hourly-rate", PROJECT_ID, USER_ID,
        "--amount", "6000", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["amount"] == 6000


# ── 1.3 User Rates ────────────────────────────────────────────────────

@responses.activate
def test_users_cost_rate(runner):
    """users cost-rate updates a user's cost rate."""
    responses.add(
        responses.PUT,
        f"{USERS_URL}/{USER_ID}/cost-rate",
        json={"amount": 4000}, status=200,
    )
    result = _invoke(runner, [
        "users", "cost-rate", USER_ID, "--amount", "4000", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["amount"] == 4000


@responses.activate
def test_users_hourly_rate(runner):
    """users hourly-rate updates a user's hourly rate."""
    responses.add(
        responses.PUT,
        f"{USERS_URL}/{USER_ID}/hourly-rate",
        json={"amount": 5500}, status=200,
    )
    result = _invoke(runner, [
        "users", "hourly-rate", USER_ID, "--amount", "5500", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["amount"] == 5500


# ── 1.4 Webhook Extras ────────────────────────────────────────────────

@responses.activate
def test_webhooks_addon_list(runner):
    """webhooks addon-list lists webhooks for an add-on."""
    hooks = [{"id": WEBHOOK_ID, "name": "Hook1"}]
    responses.add(
        responses.GET,
        f"{WS_URL}/addons/{ADDON_ID}/webhooks",
        json=hooks, status=200,
    )
    result = _invoke(runner, ["webhooks", "addon-list", ADDON_ID, "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["id"] == WEBHOOK_ID


@responses.activate
def test_webhooks_regen_token(runner):
    """webhooks regen-token regenerates a webhook secret token."""
    responses.add(
        responses.PATCH,
        f"{WEBHOOKS_URL}/{WEBHOOK_ID}/token",
        json={"token": "new-secret-token"}, status=200,
    )
    result = _invoke(runner, ["webhooks", "regen-token", WEBHOOK_ID, "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "token" in data


# ── 1.5 Expense Extras ────────────────────────────────────────────────

@responses.activate
def test_expenses_receipt(runner, tmp_path):
    """expenses receipt downloads a receipt file."""
    binary_content = b"FAKE_PDF_CONTENT"
    responses.add(
        responses.GET,
        f"{EXPENSES_URL}/{EXPENSE_ID}/files/{FILE_ID}",
        body=binary_content, status=200,
        content_type="application/octet-stream",
    )
    out_file = str(tmp_path / "receipt.pdf")
    result = _invoke(runner, [
        "expenses", "receipt", EXPENSE_ID, FILE_ID, "--output", out_file, "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["saved"] == out_file
    assert data["bytes"] == len(binary_content)


@responses.activate
def test_expense_categories_archive(runner):
    """expenses categories archive archives an expense category."""
    cat = {"id": CATEGORY_ID, "name": "Travel", "status": "ARCHIVED"}
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
    data = json.loads(result.output)
    assert data["status"] == "ARCHIVED"


# ── 1.6 Invoice Extras ────────────────────────────────────────────────

@responses.activate
def test_invoices_settings(runner):
    """invoices settings returns invoice settings."""
    settings = {"currency": "USD", "tax1": 0.0, "tax2": 0.0}
    responses.add(
        responses.GET, f"{INVOICES_URL}/settings",
        json=settings, status=200,
    )
    result = _invoke(runner, ["invoices", "settings", "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "currency" in data


@responses.activate
def test_invoices_settings_update(runner):
    """invoices settings-update updates invoice settings."""
    updated = {"currency": "EUR", "tax1": 10.0}
    responses.add(
        responses.PUT, f"{INVOICES_URL}/settings",
        json=updated, status=200,
    )
    result = _invoke(runner, [
        "invoices", "settings-update", "--currency", "EUR", "--tax1", "10.0", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["currency"] == "EUR"


@responses.activate
def test_invoices_export(runner, tmp_path):
    """invoices export saves PDF binary to file."""
    pdf_bytes = b"%PDF-1.4 fake pdf content"
    responses.add(
        responses.GET,
        f"{INVOICES_URL}/{INVOICE_ID}/export",
        body=pdf_bytes, status=200,
        content_type="application/pdf",
    )
    out_file = str(tmp_path / "invoice.pdf")
    result = _invoke(runner, [
        "invoices", "export", INVOICE_ID, "--output", out_file, "--user-locale", "en", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["saved"] == out_file
    assert data["bytes"] == len(pdf_bytes)


@responses.activate
def test_invoices_filter(runner):
    """invoices filter returns filtered invoice list."""
    invoice = {"id": INVOICE_ID, "status": "UNSENT"}
    responses.add(
        responses.POST, f"{INVOICES_URL}/info",
        json=[invoice], status=200,
    )
    result = _invoke(runner, [
        "invoices", "filter", "--status", "UNSENT", "--json",
    ])
    assert result.exit_code == 0, result.output


# ── 1.7 Time Off Extras ───────────────────────────────────────────────

@responses.activate
def test_time_off_request_delete(runner):
    """time-off request delete removes a time off request."""
    responses.add(
        responses.DELETE,
        f"{TIME_OFF_URL}/policies/{POLICY_ID}/requests/{REQUEST_ID}",
        json={}, status=200,
    )
    result = _invoke(runner, [
        "time-off", "request", "delete", POLICY_ID, REQUEST_ID, "--confirm", "--json",
    ])
    assert result.exit_code == 0, result.output


@responses.activate
def test_time_off_request_update(runner):
    """time-off request update changes request status."""
    req = {"id": REQUEST_ID, "status": "APPROVED"}
    responses.add(
        responses.PATCH,
        f"{TIME_OFF_URL}/policies/{POLICY_ID}/requests/{REQUEST_ID}",
        json=req, status=200,
    )
    result = _invoke(runner, [
        "time-off", "request", "update", POLICY_ID, REQUEST_ID,
        "--status", "APPROVED", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["status"] == "APPROVED"


@responses.activate
def test_time_off_request_create_for_user(runner):
    """time-off request create-for-user creates request for a user."""
    req = {"id": REQUEST_ID, "userId": USER_ID}
    responses.add(
        responses.POST,
        f"{TIME_OFF_URL}/policies/{POLICY_ID}/users/{USER_ID}/requests",
        json=req, status=201,
    )
    result = _invoke(runner, [
        "time-off", "request", "create-for-user", POLICY_ID, USER_ID,
        "--start", "2026-03-20", "--end", "2026-03-21", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["id"] == REQUEST_ID


@responses.activate
def test_time_off_requests_list(runner):
    """time-off requests list returns workspace time off requests."""
    req_list = [{"id": REQUEST_ID, "status": "PENDING"}]
    responses.add(
        responses.POST,
        f"{TIME_OFF_URL}/requests",
        json=req_list, status=200,
    )
    result = _invoke(runner, ["time-off", "requests", "list", "--json"])
    assert result.exit_code == 0, result.output


@responses.activate
def test_time_off_balance_policy(runner):
    """time-off balance policy returns policy balance."""
    balance = {"policyId": POLICY_ID, "balance": 10.0}
    responses.add(
        responses.GET,
        f"{TIME_OFF_URL}/balance/policy/{POLICY_ID}",
        json=balance, status=200,
    )
    result = _invoke(runner, ["time-off", "balance", "policy", POLICY_ID, "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "balance" in data


@responses.activate
def test_time_off_balance_update_policy(runner):
    """time-off balance update-policy updates policy balance per spec."""
    responses.add(
        responses.PATCH,
        f"{TIME_OFF_URL}/balance/policy/{POLICY_ID}",
        json={"ok": True}, status=200,
    )
    result = _invoke(runner, [
        "time-off", "balance", "update-policy", POLICY_ID,
        "--user-id", USER_ID, "--value", "15.0", "--json",
    ])
    assert result.exit_code == 0, result.output
    sent = json.loads(responses.calls[-1].request.body)
    assert sent["userIds"] == [USER_ID]
    assert sent["value"] == 15.0


# ── 1.8 Scheduling Extras ─────────────────────────────────────────────

@responses.activate
def test_scheduling_batch_totals(runner):
    """scheduling assignments batch-totals fetches batch project totals."""
    totals = {"totals": [{"projectId": PROJECT_ID, "totalHours": 40}]}
    responses.add(
        responses.POST,
        f"{SCHEDULING_URL}/projects/totals",
        json=totals, status=200,
    )
    result = _invoke(runner, [
        "scheduling", "assignments", "batch-totals",
        "--start", "2024-01-01", "--end", "2024-01-31",
        "--project-id", PROJECT_ID, "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "totals" in data


@responses.activate
def test_scheduling_capacity_filter(runner):
    """scheduling assignments capacity-filter fetches user capacity totals."""
    capacity = {"users": [{"userId": USER_ID, "capacity": 40}]}
    responses.add(
        responses.POST,
        f"{SCHEDULING_URL}/user-filter/totals",
        json=capacity, status=200,
    )
    result = _invoke(runner, [
        "scheduling", "assignments", "capacity-filter",
        "--start", "2024-01-01", "--end", "2024-01-31",
        "--user-id", USER_ID, "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "users" in data


# ── 1.9 Approval Extras ───────────────────────────────────────────────

@responses.activate
def test_approval_resubmit_for_user(runner):
    """approval resubmit-for-user sends periodStart body."""
    result_data = {"resubmitted": True}
    responses.add(
        responses.POST,
        f"{APPROVAL_URL}/users/{USER_ID}/resubmit-entries-for-approval",
        json=result_data, status=200,
    )
    result = _invoke(runner, [
        "approval", "resubmit-for-user", USER_ID,
        "--start", "2024-01-01", "--json",
    ])
    assert result.exit_code == 0, result.output
    req_body = json.loads(responses.calls[0].request.body)
    assert "periodStart" in req_body


# ── Part 2 — Enum verifications ───────────────────────────────────────

@responses.activate
def test_webhooks_create_trigger_choices(runner):
    """webhooks create --event accepts valid webhook event names."""
    result = runner.invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "webhooks", "create", "--url", "https://x.com", "--name", "X",
        "--event", "INVALID_EVENT",
    ])
    assert result.exit_code != 0
    assert "Invalid value" in result.output or "invalid choice" in result.output.lower()


@responses.activate
def test_invoices_status_choices(runner):
    """invoices status --status accepts UNSENT and OVERDUE."""
    result = runner.invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "invoices", "status", "someid", "--status", "DRAFT_INVALID",
    ])
    assert result.exit_code != 0


@responses.activate
def test_tasks_update_status_all(runner):
    """tasks update --status accepts ALL."""
    # Just verify the choice passes validation (no API call needed for help check)
    result = runner.invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "tasks", "update", "--help",
    ])
    assert "ALL" in result.output


@responses.activate
def test_custom_fields_create_dropdown_single(runner):
    """custom-fields create --type accepts DROPDOWN_SINGLE."""
    result = runner.invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "custom-fields", "create", "--help",
    ])
    assert "DROPDOWN_SINGLE" in result.output
    assert "DROPDOWN_MULTIPLE" in result.output


@responses.activate
def test_reports_summary_group_by_choices(runner):
    """reports summary --group-by accepts DATE, WEEK, MONTH, TASK."""
    result = runner.invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "reports", "summary", "--help",
    ])
    assert "TASK" in result.output
    assert "DATE" in result.output
    assert "WEEK" in result.output
    assert "MONTH" in result.output


@responses.activate
def test_entities_type_is_choice(runner):
    """entities created --type rejects invalid document type."""
    result = runner.invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "entities", "created",
        "--type", "INVALID_TYPE",
        "--start", "2026-03-01", "--end", "2026-03-13",
    ])
    assert result.exit_code != 0


@responses.activate
def test_time_off_policies_icon_choice(runner):
    """time-off policies create --icon appears in help."""
    result = runner.invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "time-off", "policies", "create", "--help",
    ])
    assert "UMBRELLA" in result.output or "--icon" in result.output


# ── MCP Hardening Tests ────────────────────────────────────────────────

USER_URL = f"{BASE_URL}/user"


def _add_user_mock():
    """Register mock for /user endpoint (needed when _user(ctx) resolves user ID)."""
    responses.add(
        responses.GET, USER_URL,
        json={"id": USER_ID, "defaultWorkspace": WS_ID},
        status=200,
    )


@responses.activate
def test_entries_bulk_update(runner):
    """entries bulk-update sends an array of objects, each with an id field."""
    _add_user_mock()
    entries_url = f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries"
    responses.add(responses.PUT, entries_url, json={"updated": 2}, status=200)
    result = _invoke(runner, [
        "entries", "bulk-update",
        "--ids", "abc123",
        "--ids", "def456",
        "--billable",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    # Find the PUT call
    put_call = next(c for c in responses.calls if c.request.method == "PUT")
    req_body = json.loads(put_call.request.body)
    assert isinstance(req_body, list), "Body must be an array"
    assert len(req_body) == 2
    ids_in_body = {item["id"] for item in req_body}
    assert ids_in_body == {"abc123", "def456"}
    assert all(item["billable"] is True for item in req_body)


@responses.activate
def test_invoices_export_base64(runner):
    """invoices export --base64 returns base64-encoded content as JSON."""
    import base64
    raw_bytes = b"PDF-CONTENT"
    responses.add(
        responses.GET,
        f"{BASE_URL}/workspaces/{WS_ID}/invoices/{INVOICE_ID}/export",
        body=raw_bytes,
        status=200,
        content_type="application/pdf",
    )
    result = _invoke(runner, [
        "invoices", "export", INVOICE_ID,
        "--user-locale", "en", "--base64", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["content_base64"] == base64.b64encode(raw_bytes).decode()
    assert data["bytes"] == len(raw_bytes)


@responses.activate
def test_expenses_receipt_base64(runner):
    """expenses receipt --base64 returns base64-encoded content as JSON."""
    import base64
    raw_bytes = b"RECEIPT-BYTES"
    responses.add(
        responses.GET,
        f"{BASE_URL}/workspaces/{WS_ID}/expenses/{EXPENSE_ID}/files/{FILE_ID}",
        body=raw_bytes,
        status=200,
        content_type="application/octet-stream",
    )
    result = _invoke(runner, [
        "expenses", "receipt", EXPENSE_ID, FILE_ID,
        "--base64", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["content_base64"] == base64.b64encode(raw_bytes).decode()
    assert data["bytes"] == len(raw_bytes)


@responses.activate
def test_entries_list_limit(runner):
    """entries list --limit 2 returns only 2 items."""
    _add_user_mock()
    entries_url = f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries"
    all_entries = [{"id": f"e{i}", "description": f"Entry {i}"} for i in range(5)]
    responses.add(
        responses.GET, entries_url,
        json=all_entries,
        status=200,
        headers={"Last-Page": "true"},
    )
    result = _invoke(runner, [
        "entries", "list", "--limit", "2", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert len(data) == 2


@responses.activate
def test_entries_list_page(runner):
    """entries list --page 2 --page-size 10 does a single-page fetch."""
    _add_user_mock()
    entries_url = f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries"
    page_entries = [{"id": f"e{i}", "description": f"Entry {i}"} for i in range(10)]
    responses.add(
        responses.GET, entries_url,
        json=page_entries,
        status=200,
    )
    result = _invoke(runner, [
        "entries", "list", "--page", "2", "--page-size", "10", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert len(data) == 10
    # Find the entries GET call (skip /user call)
    entries_call = next(c for c in responses.calls if "time-entries" in c.request.url)
    assert "page=2" in entries_call.request.url
    assert "page-size=10" in entries_call.request.url


@responses.activate
def test_assignments_no_print(runner):
    """assignments list --json outputs clean JSON with no print() bleed."""
    assignment = {
        "id": "assign111111111111111111",
        "projectId": PROJECT_ID,
        "userId": USER_ID,
        "start": "2026-03-01T00:00:00Z",
        "end": "2026-03-05T00:00:00Z",
        "totalBillableHours": 8,
    }
    responses.add(
        responses.GET,
        f"{BASE_URL}/workspaces/{WS_ID}/scheduling/assignments/all",
        json=[assignment],
        status=200,
    )
    result = _invoke(runner, [
        "scheduling", "assignments", "list",
        "--start", "2024-01-01", "--end", "2024-12-31", "--json",
    ])
    assert result.exit_code == 0, result.output
    # Should be valid JSON (no stray print() output mixed in)
    data = json.loads(result.output)


# ── New tests: delete-recurring --json and commands manifest ───────────


ASGN_ID = "asgn1111111111111111111111"


@responses.activate
def test_assignments_delete_recurring_json(runner):
    """assignments delete-recurring --json --confirm exits 0 and returns JSON."""
    url = f"{BASE_URL}/workspaces/{WS_ID}/scheduling/assignments/recurring/{ASGN_ID}"
    responses.add(responses.DELETE, url, json={}, status=200)
    result = _invoke(runner, [
        "scheduling", "assignments", "delete-recurring", ASGN_ID,
        "--confirm", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, dict)


def test_commands_manifest(runner):
    """clockify commands --json returns a list of command schemas."""
    result = runner.invoke(__import__(
        "cli_anything.clockify.clockify_cli", fromlist=["main"]
    ).main, ["commands", "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 161, f"Expected 161 commands, got {len(data)}"
    groups = {entry["group"] for entry in data}
    assert "entries" in groups
    assert "projects" in groups
    for entry in data:
        assert "name" in entry
        assert "group" in entry
        assert "options" in entry


# ── 3.1 Report Enum Corrections ──────────────────────────────────────


def test_reports_summary_approval_state_spec_enum(runner):
    """reports summary --approval-state uses spec enum APPROVED/UNAPPROVED/ALL."""
    result = runner.invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "reports", "summary", "--help",
    ])
    # Spec-correct values must appear
    assert "UNAPPROVED" in result.output
    # Old wrong values must NOT appear
    assert "WITHDRAWN_APPROVAL" not in result.output


def test_reports_weekly_approval_state_spec_enum(runner):
    """reports weekly --approval-state uses spec enum APPROVED/UNAPPROVED/ALL."""
    result = runner.invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "reports", "weekly", "--help",
    ])
    assert "UNAPPROVED" in result.output
    assert "WITHDRAWN_APPROVAL" not in result.output


def test_reports_summary_invoicing_state_includes_all(runner):
    """reports summary --invoicing-state includes ALL value per spec."""
    result = runner.invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "reports", "summary", "--help",
    ])
    help_text = result.output
    idx = help_text.find("invoicing-state")
    assert idx > -1
    section = help_text[idx:idx + 200]
    assert "ALL" in section


def test_reports_weekly_invoicing_state_includes_all(runner):
    """reports weekly --invoicing-state includes ALL value per spec."""
    result = runner.invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "reports", "weekly", "--help",
    ])
    help_text = result.output
    idx = help_text.find("invoicing-state")
    assert idx > -1
    section = help_text[idx:idx + 200]
    assert "ALL" in section


def test_reports_amount_shown_export_choice(runner):
    """reports detailed/summary/weekly --amount-shown includes EXPORT per spec."""
    for subcmd in ("detailed", "summary", "weekly"):
        result = runner.invoke(main, [
            "--api-key", API_KEY, "--workspace", WS_ID,
            "reports", subcmd, "--help",
        ])
        assert "EXPORT" in result.output, f"EXPORT missing from reports {subcmd} --help"


@responses.activate
def test_reports_summary_approval_unapproved_accepted(runner):
    """reports summary --approval-state UNAPPROVED passes validation."""
    from cli_anything.clockify.tests.conftest import REPORTS_URL
    responses.add(
        responses.POST,
        f"{REPORTS_URL}/workspaces/{WS_ID}/reports/summary",
        json={"totals": [], "groupOne": []}, status=200,
    )
    result = _invoke(runner, [
        "reports", "summary",
        "--start", "2024-01-01", "--end", "2024-01-31",
        "--approval-state", "UNAPPROVED", "--json",
    ])
    assert result.exit_code == 0, result.output


# ── 3.2 Scheduling Required Params ───────────────────────────────────


def test_scheduling_batch_totals_requires_start_end(runner):
    """scheduling assignments batch-totals requires --start and --end."""
    result = _invoke(runner, [
        "scheduling", "assignments", "batch-totals", "--json",
    ])
    assert result.exit_code != 0
    assert "start" in result.output.lower() or "Missing" in result.output


def test_scheduling_capacity_filter_requires_start_end(runner):
    """scheduling assignments capacity-filter requires --start and --end."""
    result = _invoke(runner, [
        "scheduling", "assignments", "capacity-filter", "--json",
    ])
    assert result.exit_code != 0
    assert "start" in result.output.lower() or "Missing" in result.output


@responses.activate
def test_scheduling_batch_totals_sends_start_end_in_body(runner):
    """scheduling assignments batch-totals includes start/end in POST body."""
    responses.add(
        responses.POST,
        f"{SCHEDULING_URL}/projects/totals",
        json={"totals": []}, status=200,
    )
    result = _invoke(runner, [
        "scheduling", "assignments", "batch-totals",
        "--start", "2024-01-01", "--end", "2024-01-31",
        "--project-id", PROJECT_ID, "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["start"] == "2024-01-01"
    assert body["end"] == "2024-01-31"


@responses.activate
def test_scheduling_capacity_filter_sends_start_end_in_body(runner):
    """scheduling assignments capacity-filter includes start/end in POST body."""
    responses.add(
        responses.POST,
        f"{SCHEDULING_URL}/user-filter/totals",
        json={"users": []}, status=200,
    )
    result = _invoke(runner, [
        "scheduling", "assignments", "capacity-filter",
        "--start", "2024-01-01", "--end", "2024-01-31",
        "--user-id", USER_ID, "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["start"] == "2024-01-01"
    assert body["end"] == "2024-01-31"


# ── 3.3 Users Filter Enrichment ──────────────────────────────────────


@responses.activate
def test_users_filter_full_params(runner):
    """users filter sends all spec body fields."""
    responses.add(
        responses.POST,
        f"{USERS_URL}/info",
        json=[{"id": USER_ID, "name": "Test"}], status=200,
    )
    result = _invoke(runner, [
        "users", "filter",
        "--name", "John",
        "--email", "john@example.com",
        "--status", "ACTIVE",
        "--role", "TEAM_MANAGER",
        "--memberships", "ALL",
        "--include-roles",
        "--sort-column", "NAME",
        "--sort-order", "ASCENDING",
        "--page", "1",
        "--page-size", "25",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["name"] == "John"
    assert body["email"] == "john@example.com"
    assert body["status"] == "ACTIVE"
    assert body["roles"] == ["TEAM_MANAGER"]
    assert body["memberships"] == "ALL"
    assert body["includeRoles"] is True
    assert body["sortColumn"] == "NAME"
    assert body["sortOrder"] == "ASCENDING"
    assert body["page"] == 1
    assert body["pageSize"] == 25


# ── 3.4 Users Update Profile Enrichment ──────────────────────────────


@responses.activate
def test_users_update_profile_full_params(runner):
    """users update-profile sends all spec body fields."""
    responses.add(
        responses.PATCH,
        f"{BASE_URL}/workspaces/{WS_ID}/member-profile/{USER_ID}",
        json={"id": USER_ID}, status=200,
    )
    result = _invoke(runner, [
        "users", "update-profile", USER_ID,
        "--name", "New Name",
        "--week-start", "MONDAY",
        "--work-capacity", "PT8H",
        "--working-day", "MONDAY",
        "--working-day", "TUESDAY",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["name"] == "New Name"
    assert body["weekStart"] == "MONDAY"
    assert body["workCapacity"] == "PT8H"
    assert body["workingDays"] == ["MONDAY", "TUESDAY"]


# ── 3.5 Entries customAttributes ──────────────────────────────────────

ENTRIES_URL = f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries"
ENTRIES_DIRECT_URL = f"{BASE_URL}/workspaces/{WS_ID}/time-entries"


@responses.activate
def test_entries_add_custom_attributes(runner):
    """entries add --custom-attribute sends customAttributes in body."""
    _add_user_mock()
    responses.add(
        responses.POST, ENTRIES_URL,
        json={"id": "newentry111111111111111111"}, status=201,
    )
    result = _invoke(runner, [
        "entries", "add",
        "--start", "2024-01-01 09:00",
        "--end", "2024-01-01 10:00",
        "--custom-attribute", "myns:myname=myvalue",
        "--custom-attribute", "ns2:attr2=val2",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[-1].request.body)
    assert "customAttributes" in body
    assert len(body["customAttributes"]) == 2
    assert body["customAttributes"][0] == {
        "namespace": "myns", "name": "myname", "value": "myvalue"
    }
    assert body["customAttributes"][1] == {
        "namespace": "ns2", "name": "attr2", "value": "val2"
    }


@responses.activate
def test_entries_add_direct_custom_attributes(runner):
    """entries add-direct --custom-attribute sends customAttributes in body."""
    responses.add(
        responses.POST, ENTRIES_DIRECT_URL,
        json={"id": "newentry222222222222222222"}, status=201,
    )
    result = _invoke(runner, [
        "entries", "add-direct",
        "--start", "2024-01-01 09:00",
        "--end", "2024-01-01 10:00",
        "--custom-attribute", "testns:testname=testval",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[-1].request.body)
    assert "customAttributes" in body
    assert len(body["customAttributes"]) == 1
    assert body["customAttributes"][0]["namespace"] == "testns"
    assert body["customAttributes"][0]["name"] == "testname"
    assert body["customAttributes"][0]["value"] == "testval"


def test_entries_add_custom_attribute_bad_format(runner):
    """entries add --custom-attribute rejects bad format (no colon)."""
    result = _invoke(runner, [
        "entries", "add",
        "--start", "2024-01-01 09:00",
        "--end", "2024-01-01 10:00",
        "--custom-attribute", "bad_no_colon=value",
        "--json",
    ])
    assert result.exit_code != 0


# ── 3.6 Holidays update required fields ───────────────────────────────

HOLIDAYS_URL_CLI = f"{BASE_URL}/workspaces/{WS_ID}/holidays"
HOL_ID = "hol1111111111111111111111"


def test_holidays_update_requires_name(runner):
    """holidays update rejects missing --name."""
    result = _invoke(runner, [
        "holidays", "update", HOL_ID,
        "--date", "2024-01-01", "--recurring", "--json",
    ])
    assert result.exit_code != 0


def test_holidays_update_requires_date(runner):
    """holidays update rejects missing --date."""
    result = _invoke(runner, [
        "holidays", "update", HOL_ID,
        "--name", "NY", "--recurring", "--json",
    ])
    assert result.exit_code != 0


def test_holidays_update_requires_recurring(runner):
    """holidays update rejects missing --recurring/--no-recurring."""
    result = _invoke(runner, [
        "holidays", "update", HOL_ID,
        "--name", "NY", "--date", "2024-01-01", "--json",
    ])
    assert result.exit_code != 0


@responses.activate
def test_holidays_update_sends_required_fields(runner):
    """holidays update sends name, datePeriod, occursAnnually in body."""
    responses.add(
        responses.PUT, f"{HOLIDAYS_URL_CLI}/{HOL_ID}",
        json={"id": HOL_ID}, status=200,
    )
    result = _invoke(runner, [
        "holidays", "update", HOL_ID,
        "--name", "New Year", "--date", "2024-01-01",
        "--recurring", "--color", "#FF0000", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["name"] == "New Year"
    assert body["occursAnnually"] is True
    assert "datePeriod" in body
    assert body["datePeriod"]["startDate"] == "2024-01-01T00:00:00Z"
    assert body["color"] == "#FF0000"


# ── 3.7 Custom fields update required fields ──────────────────────────

CF_URL = f"{BASE_URL}/workspaces/{WS_ID}/custom-fields"


def test_custom_fields_update_requires_name(runner):
    """custom-fields update rejects missing --name."""
    result = _invoke(runner, [
        "custom-fields", "update", "cf111111111111111111111",
        "--field-type", "TXT", "--json",
    ])
    assert result.exit_code != 0


def test_custom_fields_update_requires_field_type(runner):
    """custom-fields update rejects missing --field-type."""
    result = _invoke(runner, [
        "custom-fields", "update", "cf111111111111111111111",
        "--name", "Test", "--json",
    ])
    assert result.exit_code != 0


@responses.activate
def test_custom_fields_update_sends_required_fields(runner):
    """custom-fields update sends name and type in body."""
    cf_id = "cf111111111111111111111"
    responses.add(
        responses.PUT, f"{CF_URL}/{cf_id}",
        json={"id": cf_id}, status=200,
    )
    result = _invoke(runner, [
        "custom-fields", "update", cf_id,
        "--name", "Budget", "--field-type", "NUMBER",
        "--required", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["name"] == "Budget"
    assert body["type"] == "NUMBER"
    assert body["required"] is True


# ── 3.8 Entities optional dates ───────────────────────────────────────


@responses.activate
def test_entities_created_no_dates(runner):
    """entities created works without --start/--end (optional per spec)."""
    entities_created_url = f"{BASE_URL}/workspaces/{WS_ID}/entities/created"
    responses.add(
        responses.GET, entities_created_url,
        json=[{"id": "e1", "entityType": "TIME_ENTRY", "changedAt": "2026-03-13T10:00:00Z"}],
        status=200, match_querystring=False,
    )
    result = _invoke(runner, [
        "entities", "created", "--type", "TIME_ENTRY", "--json",
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert len(data) == 1
    # Verify no start/end in query string
    req_url = responses.calls[0].request.url
    assert "start=" not in req_url
    assert "end=" not in req_url


@responses.activate
def test_entities_multi_type(runner):
    """entities created --type A --type B sends comma-joined type param."""
    entities_created_url = f"{BASE_URL}/workspaces/{WS_ID}/entities/created"
    responses.add(
        responses.GET, entities_created_url,
        json=[], status=200, match_querystring=False,
    )
    result = _invoke(runner, [
        "entities", "created",
        "--type", "TIME_ENTRY", "--type", "TIME_ENTRY_RATE",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    req_url = responses.calls[0].request.url
    # The types should be comma-joined in the type param
    assert "TIME_ENTRY" in req_url
    assert "TIME_ENTRY_RATE" in req_url


# ── 3.9 Scheduling list/publish require start/end ────────────────────


def test_assignments_list_requires_start_end(runner):
    """scheduling assignments list requires --start and --end."""
    result = _invoke(runner, [
        "scheduling", "assignments", "list", "--json",
    ])
    assert result.exit_code != 0


def test_assignments_publish_requires_start_end(runner):
    """scheduling assignments publish requires --start and --end."""
    result = _invoke(runner, [
        "scheduling", "assignments", "publish", "--json",
    ])
    assert result.exit_code != 0


@responses.activate
def test_assignments_publish_sends_start_end_in_body(runner):
    """scheduling assignments publish sends start/end in PUT body."""
    responses.add(
        responses.PUT,
        f"{BASE_URL}/workspaces/{WS_ID}/scheduling/assignments/publish",
        json={}, status=200,
    )
    result = _invoke(runner, [
        "scheduling", "assignments", "publish",
        "--start", "2024-01-01", "--end", "2024-01-31", "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert body["start"] == "2024-01-01"
    assert body["end"] == "2024-01-31"


# ── 3.10 Users update-profile userCustomFields ────────────────────────


@responses.activate
def test_users_update_profile_custom_fields(runner):
    """users update-profile --custom-field sends userCustomFields in body."""
    responses.add(
        responses.PATCH,
        f"{BASE_URL}/workspaces/{WS_ID}/member-profile/{USER_ID}",
        json={"id": USER_ID}, status=200,
    )
    result = _invoke(runner, [
        "users", "update-profile", USER_ID,
        "--name", "Test",
        "--custom-field", "cf123=SomeValue",
        "--custom-field", "cf456=OtherValue",
        "--json",
    ])
    assert result.exit_code == 0, result.output
    body = json.loads(responses.calls[0].request.body)
    assert "userCustomFields" in body
    assert len(body["userCustomFields"]) == 2
    assert body["userCustomFields"][0] == {"customFieldId": "cf123", "value": "SomeValue"}
    assert body["userCustomFields"][1] == {"customFieldId": "cf456", "value": "OtherValue"}
