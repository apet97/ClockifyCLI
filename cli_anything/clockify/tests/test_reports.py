"""Tests for report operations.

Key checks:
- Reports URL (not base URL) is used
- Date format includes milliseconds (.000Z)
"""

from __future__ import annotations

import json as jsonlib
import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, REPORTS_URL, WS_ID, USER_ID, API_KEY,
)

DETAILED_URL = f"{REPORTS_URL}/workspaces/{WS_ID}/reports/detailed"
SUMMARY_URL = f"{REPORTS_URL}/workspaces/{WS_ID}/reports/summary"
WEEKLY_URL = f"{REPORTS_URL}/workspaces/{WS_ID}/reports/weekly"


@responses.activate
def test_detailed_report_uses_reports_url(backend):
    """Report must POST to REPORTS_URL, not BASE_URL."""
    mock_response = {"timeentries": [], "totals": [{"totalTime": 0}]}
    responses.add(responses.POST, DETAILED_URL, json=mock_response, status=200)

    backend.report_detailed(
        WS_ID, "2026-03-01T00:00:00Z", "2026-03-13T23:59:59Z"
    )

    assert len(responses.calls) == 1
    req = responses.calls[0].request
    # Must use reports URL, not base
    assert REPORTS_URL in req.url
    assert BASE_URL not in req.url


@responses.activate
def test_detailed_report_date_has_milliseconds(backend):
    """Report body dates must include milliseconds (.000Z)."""
    mock_response = {"timeentries": [], "totals": []}
    responses.add(responses.POST, DETAILED_URL, json=mock_response, status=200)

    backend.report_detailed(
        WS_ID, "2026-03-01T00:00:00Z", "2026-03-13T23:59:59Z"
    )

    req = responses.calls[0].request
    body = jsonlib.loads(req.body)
    assert ".000Z" in body["dateRangeStart"] or ".999Z" in body["dateRangeEnd"]
    # Check milliseconds format
    assert body["dateRangeStart"].endswith("Z")
    assert "." in body["dateRangeStart"]


@responses.activate
def test_summary_report_uses_reports_url(backend):
    mock_response = {"groupOne": [], "totals": [{"totalTime": 3600}]}
    responses.add(responses.POST, SUMMARY_URL, json=mock_response, status=200)

    backend.report_summary(WS_ID, "2026-03-01T00:00:00Z", "2026-03-13T23:59:59Z")

    req = responses.calls[0].request
    assert REPORTS_URL in req.url
    body = jsonlib.loads(req.body)
    assert "summaryFilter" in body
    assert "dateRangeStart" in body


@responses.activate
def test_weekly_report_uses_reports_url(backend):
    mock_response = {"weeklyEntries": [], "totals": []}
    responses.add(responses.POST, WEEKLY_URL, json=mock_response, status=200)

    backend.report_weekly(WS_ID, "2026-03-01T00:00:00Z", "2026-03-13T23:59:59Z")

    req = responses.calls[0].request
    assert REPORTS_URL in req.url
    body = jsonlib.loads(req.body)
    assert "weeklyFilter" in body


# ── CLI test ──────────────────────────────────────────────────────────

@responses.activate
def test_cli_reports_summary_json(runner, session):
    from cli_anything.clockify.clockify_cli import main

    mock_response = {"groupOne": [{"name": "My Project", "duration": 3600}], "totals": [{"totalTime": 3600}]}
    responses.add(responses.POST, SUMMARY_URL, json=mock_response, status=200)

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "reports", "summary",
        "--start", "2026-03-01",
        "--end", "2026-03-13",
        "--json",
    ])
    assert result.exit_code == 0
    data = jsonlib.loads(result.output)
    assert "groupOne" in data


# ── new parameter coverage tests ──────────────────────────────────────

EXPENSE_URL = f"{REPORTS_URL}/workspaces/{WS_ID}/reports/expenses/detailed"


@responses.activate
def test_detailed_report_forwards_new_filters(backend):
    """New filter params (tasks, userGroups, archived, amountShown, rounding, timeZone) appear in POST body."""
    responses.add(responses.POST, DETAILED_URL, json={"timeentries": [], "totals": []}, status=200)

    backend.report_detailed(
        WS_ID, "2026-03-01T00:00:00Z", "2026-03-15T23:59:59Z",
        task_ids=["t1", "t2"],
        user_group_ids=["g1"],
        archived=True,
        amount_shown="EARNED",
        rounding=True,
        timezone="UTC",
    )

    body = jsonlib.loads(responses.calls[0].request.body)
    assert body["tasks"] == {"ids": ["t1", "t2"], "contains": "CONTAINS"}
    assert body["userGroups"] == {"ids": ["g1"], "contains": "CONTAINS"}
    assert body["archived"] == "All"
    assert body["amountShown"] == "EARNED"
    assert body["rounding"] is True
    assert body["timeZone"] == "UTC"


@responses.activate
def test_summary_report_sort_order(backend):
    """sort_order is forwarded as sortOrder in summary report body."""
    responses.add(responses.POST, SUMMARY_URL, json={"groupOne": [], "totals": []}, status=200)

    backend.report_summary(
        WS_ID, "2026-03-01T00:00:00Z", "2026-03-15T23:59:59Z",
        sort_order="DESCENDING",
    )

    body = jsonlib.loads(responses.calls[0].request.body)
    assert body["sortOrder"] == "DESCENDING"


@responses.activate
def test_expense_report_forwards_filters(backend):
    """Expense report forwards users, projects, categories filters."""
    responses.add(responses.POST, EXPENSE_URL, json={"expenses": [], "totals": []}, status=200)

    backend.report_expense(
        WS_ID, "2026-03-01T00:00:00Z", "2026-03-15T23:59:59Z",
        user_ids=["u1"],
        project_ids=["p1", "p2"],
        category_ids=["cat1"],
    )

    body = jsonlib.loads(responses.calls[0].request.body)
    assert body["users"] == {"ids": ["u1"], "contains": "CONTAINS"}
    assert body["projects"] == {"ids": ["p1", "p2"], "contains": "CONTAINS"}
    assert body["categories"] == {"ids": ["cat1"], "contains": "CONTAINS"}


@responses.activate
def test_cli_detailed_task_filter(runner, session):
    """CLI --task and --user-group options are forwarded in request body."""
    from cli_anything.clockify.clockify_cli import main

    responses.add(responses.POST, DETAILED_URL, json={"timeentries": [], "totals": []}, status=200)

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "reports", "detailed",
        "--start", "2026-03-01",
        "--end", "2026-03-15",
        "--task", "T1",
        "--user-group", "G1",
        "--archived",
        "--timezone", "UTC",
        "--json",
    ])
    assert result.exit_code == 0
    body = jsonlib.loads(responses.calls[0].request.body)
    assert body["tasks"] == {"ids": ["T1"], "contains": "CONTAINS"}
    assert body["userGroups"] == {"ids": ["G1"], "contains": "CONTAINS"}
    assert body["archived"] == "All"
    assert body["timeZone"] == "UTC"
