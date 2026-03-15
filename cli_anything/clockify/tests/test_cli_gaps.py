"""Tests for CLI commands added in the gaps pass."""

from __future__ import annotations

import json
import responses

from click.testing import CliRunner

from cli_anything.clockify.tests.conftest import BASE_URL, WS_ID, API_KEY
from cli_anything.clockify.clockify_cli import main

CLIENTS_URL = f"{BASE_URL}/workspaces/{WS_ID}/clients"
TAGS_URL = f"{BASE_URL}/workspaces/{WS_ID}/tags"
PROJECTS_URL = f"{BASE_URL}/workspaces/{WS_ID}/projects"
INVOICES_URL = f"{BASE_URL}/workspaces/{WS_ID}/invoices"
TIME_OFF_POLICIES_URL = f"{BASE_URL}/workspaces/{WS_ID}/time-off/policies"
EXPENSES_URL = f"{BASE_URL}/workspaces/{WS_ID}/expenses"

CLIENT_ID = "client11111111111111111111"
TAG_ID = "tag1111111111111111111111"
TASK_ID = "task111111111111111111111"
PROJECT_ID = "proj111111111111111111111"
INVOICE_ID = "inv1111111111111111111111"
POLICY_ID = "pol1111111111111111111111"
EXPENSE_ID = "exp1111111111111111111111"


@responses.activate
def test_clients_get(runner):
    """clients get <id> returns client JSON."""
    client = {"id": CLIENT_ID, "name": "Test Client", "workspaceId": WS_ID}
    responses.add(
        responses.GET, f"{CLIENTS_URL}/{CLIENT_ID}",
        json=client, status=200,
    )
    result = runner.invoke(main, [
        "--api-key", API_KEY,
        "--workspace", WS_ID,
        "clients", "get", CLIENT_ID, "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["id"] == CLIENT_ID


@responses.activate
def test_tags_get(runner):
    """tags get <id> returns tag JSON."""
    tag = {"id": TAG_ID, "name": "billable", "workspaceId": WS_ID}
    responses.add(
        responses.GET, f"{TAGS_URL}/{TAG_ID}",
        json=tag, status=200,
    )
    result = runner.invoke(main, [
        "--api-key", API_KEY,
        "--workspace", WS_ID,
        "tags", "get", TAG_ID, "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["id"] == TAG_ID


@responses.activate
def test_tasks_get(runner):
    """tasks get <id> --project <project_id> returns task JSON."""
    task = {
        "id": TASK_ID,
        "name": "Backend",
        "status": "ACTIVE",
        "projectId": PROJECT_ID,
        "duration": "PT0S",
    }
    responses.add(
        responses.GET,
        f"{PROJECTS_URL}/{PROJECT_ID}/tasks/{TASK_ID}",
        json=task, status=200,
    )
    result = runner.invoke(main, [
        "--api-key", API_KEY,
        "--workspace", WS_ID,
        "tasks", "get", TASK_ID, "--project", PROJECT_ID, "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["id"] == TASK_ID


@responses.activate
def test_invoices_create(runner):
    """invoices create --json returns created invoice with 'id' key."""
    invoice = {
        "id": INVOICE_ID,
        "invoiceNumber": "INV-001",
        "status": "DRAFT",
        "workspaceId": WS_ID,
    }
    responses.add(responses.POST, INVOICES_URL, json=invoice, status=201)
    result = runner.invoke(main, [
        "--api-key", API_KEY,
        "--workspace", WS_ID,
        "invoices", "create", "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "id" in data
    assert data["id"] == INVOICE_ID


@responses.activate
def test_invoices_update(runner):
    """invoices update <id> --json returns updated invoice."""
    invoice = {
        "id": INVOICE_ID,
        "status": "SENT",
        "workspaceId": WS_ID,
    }
    responses.add(
        responses.PUT, f"{INVOICES_URL}/{INVOICE_ID}",
        json=invoice, status=200,
    )
    result = runner.invoke(main, [
        "--api-key", API_KEY,
        "--workspace", WS_ID,
        "invoices", "update", INVOICE_ID, "--note", "Updated", "--json",
    ])
    assert result.exit_code == 0


@responses.activate
def test_time_off_policies_create(runner):
    """time-off policies create --name 'Annual' --json returns policy."""
    policy = {
        "id": POLICY_ID,
        "name": "Annual",
        "timeOffType": "VACATION",
        "isActive": True,
        "workspaceId": WS_ID,
    }
    responses.add(responses.POST, TIME_OFF_POLICIES_URL, json=policy, status=201)
    result = runner.invoke(main, [
        "--api-key", API_KEY,
        "--workspace", WS_ID,
        "time-off", "policies", "create",
        "--name", "Annual",
        "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["name"] == "Annual"


@responses.activate
def test_time_off_policies_update(runner):
    """time-off policies update <id> --json returns updated policy."""
    policy = {
        "id": POLICY_ID,
        "name": "Annual Leave",
        "workspaceId": WS_ID,
    }
    responses.add(
        responses.PUT, f"{TIME_OFF_POLICIES_URL}/{POLICY_ID}",
        json=policy, status=200,
    )
    result = runner.invoke(main, [
        "--api-key", API_KEY,
        "--workspace", WS_ID,
        "time-off", "policies", "update", POLICY_ID,
        "--name", "Annual Leave",
        "--json",
    ])
    assert result.exit_code == 0


@responses.activate
def test_expenses_update(runner):
    """expenses update <id> --json returns updated expense."""
    expense = {
        "id": EXPENSE_ID,
        "unitPrice": 75.0,
        "notes": "Updated",
        "workspaceId": WS_ID,
    }
    responses.add(
        responses.PUT, f"{EXPENSES_URL}/{EXPENSE_ID}",
        json=expense, status=200,
    )
    result = runner.invoke(main, [
        "--api-key", API_KEY,
        "--workspace", WS_ID,
        "expenses", "update", EXPENSE_ID,
        "--amount", "75.0",
        "--notes", "Updated",
        "--json",
    ])
    assert result.exit_code == 0
