"""Shared fixtures for Clockify CLI tests."""

from __future__ import annotations

import pytest
import responses as resp_lib
from click.testing import CliRunner

from cli_anything.clockify.utils.session import Session
from cli_anything.clockify.core.clockify_backend import ClockifyBackend


BASE_URL = "https://api.clockify.me/api/v1"
REPORTS_URL = "https://reports.api.clockify.me/v1"
WS_ID = "ws111111111111111111111111"
USER_ID = "user222222222222222222222222"
API_KEY = "test-api-key-12345"


@pytest.fixture
def session():
    s = Session(
        api_key=API_KEY,
        workspace_id=WS_ID,
        base_url=BASE_URL,
        reports_url=REPORTS_URL,
    )
    s.user_id = USER_ID
    return s


@pytest.fixture
def backend(session):
    return ClockifyBackend(session)


@pytest.fixture
def runner():
    return CliRunner()


# ── Data factories ────────────────────────────────────────────────────

def make_time_entry(
    entry_id: str = "entry111111111111111111111",
    description: str = "Test work",
    start: str = "2026-03-13T09:00:00Z",
    end: str | None = "2026-03-13T10:00:00Z",
    project_id: str | None = None,
) -> dict:
    ti: dict = {"start": start, "duration": "PT1H0M0S"}
    if end:
        ti["end"] = end
    else:
        ti["duration"] = None
    entry: dict = {
        "id": entry_id,
        "description": description,
        "timeInterval": ti,
        "workspaceId": WS_ID,
        "userId": USER_ID,
    }
    if project_id:
        entry["projectId"] = project_id
    return entry


def make_project(
    project_id: str = "proj111111111111111111111",
    name: str = "Test Project",
    color: str = "#FF0000",
    archived: bool = False,
) -> dict:
    return {
        "id": project_id,
        "name": name,
        "color": color,
        "archived": archived,
        "workspaceId": WS_ID,
    }


def make_workspace(
    ws_id: str = WS_ID,
    name: str = "My Workspace",
) -> dict:
    return {
        "id": ws_id,
        "name": name,
        "currency": {"code": "USD"},
    }


def make_client(
    client_id: str = "client11111111111111111111",
    name: str = "Test Client",
) -> dict:
    return {"id": client_id, "name": name, "workspaceId": WS_ID}


def make_tag(
    tag_id: str = "tag1111111111111111111111",
    name: str = "billable",
) -> dict:
    return {"id": tag_id, "name": name, "workspaceId": WS_ID}


def make_task(
    task_id: str = "task111111111111111111111",
    project_id: str = "proj111111111111111111111",
    name: str = "Backend",
    status: str = "ACTIVE",
) -> dict:
    return {
        "id": task_id,
        "name": name,
        "status": status,
        "projectId": project_id,
        "duration": "PT0S",
    }


def make_user(
    user_id: str = USER_ID,
    name: str = "Test User",
    email: str = "test@example.com",
) -> dict:
    return {
        "id": user_id,
        "name": name,
        "email": email,
        "status": "ACTIVE",
        "defaultWorkspace": WS_ID,
    }


def make_webhook(
    webhook_id: str = "hook111111111111111111111",
    name: str = "Test Hook",
    url: str = "https://example.com/hook",
    trigger: str = "NEW_TIME_ENTRY",
) -> dict:
    return {
        "id": webhook_id,
        "name": name,
        "url": url,
        "triggerSourceType": trigger,
        "workspaceId": WS_ID,
    }


def make_approval(
    approval_id: str = "appr111111111111111111111",
    status: str = "PENDING",
) -> dict:
    return {
        "id": approval_id,
        "status": status,
        "ownerId": USER_ID,
        "dateRangeStart": "2026-03-01T00:00:00Z",
        "dateRangeEnd": "2026-03-07T23:59:59Z",
        "workspaceId": WS_ID,
    }


def make_group(
    group_id: str = "grp1111111111111111111111",
    name: str = "Test Group",
    user_ids: list | None = None,
) -> dict:
    return {
        "id": group_id,
        "name": name,
        "userIds": user_ids or [],
        "workspaceId": WS_ID,
    }


def make_expense(
    expense_id: str = "exp1111111111111111111111",
    category_name: str = "Travel",
    amount: float = 50.0,
    date: str = "2026-03-13T00:00:00Z",
) -> dict:
    return {
        "id": expense_id,
        "categoryName": category_name,
        "quantity": 1,
        "unitPrice": amount,
        "date": date,
        "notes": "",
        "workspaceId": WS_ID,
        "userId": USER_ID,
    }


def make_holiday(
    holiday_id: str = "hol1111111111111111111111",
    name: str = "New Year",
    date: str = "2026-01-01T00:00:00Z",
    recurring: bool = True,
) -> dict:
    return {
        "id": holiday_id,
        "name": name,
        "date": date,
        "recurring": recurring,
        "workspaceId": WS_ID,
    }


def make_invoice(
    invoice_id: str = "inv1111111111111111111111",
    invoice_number: str = "INV-001",
    status: str = "DRAFT",
    client_name: str = "Acme Corp",
) -> dict:
    return {
        "id": invoice_id,
        "invoiceNumber": invoice_number,
        "status": status,
        "clientName": client_name,
        "total": 1000.0,
        "workspaceId": WS_ID,
    }


def make_time_off_policy(
    policy_id: str = "pol1111111111111111111111",
    name: str = "Annual Leave",
    time_off_type: str = "VACATION",
) -> dict:
    return {
        "id": policy_id,
        "name": name,
        "timeOffType": time_off_type,
        "isActive": True,
        "workspaceId": WS_ID,
    }


def make_custom_field(
    field_id: str = "cf11111111111111111111111",
    name: str = "Ticket #",
    field_type: str = "TXT",
) -> dict:
    return {
        "id": field_id,
        "name": name,
        "type": field_type,
        "status": "ACTIVE",
        "workspaceId": WS_ID,
    }


def make_assignment(
    assignment_id: str = "asgn1111111111111111111111",
    project_id: str = "proj111111111111111111111111",
    user_id: str = "user222222222222222222222222",
    start: str = "2026-03-13",
    end: str = "2026-03-20",
    hours_per_day: float = 8.0,
) -> dict:
    return {
        "id": assignment_id,
        "projectId": project_id,
        "userId": user_id,
        "start": start,
        "end": end,
        "hoursPerDay": hours_per_day,
        "totalBillableHours": hours_per_day * 5,
    }
