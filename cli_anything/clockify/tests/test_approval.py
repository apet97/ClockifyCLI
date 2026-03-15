"""Tests for approval request operations."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, USER_ID, API_KEY,
    make_approval,
)

APPROVALS_URL = f"{BASE_URL}/workspaces/{WS_ID}/approval-requests"


@responses.activate
def test_list_approvals(backend):
    """list_approvals returns list."""
    approvals = [make_approval("a1"), make_approval("a2")]
    responses.add(responses.GET, APPROVALS_URL, json=approvals, status=200)
    result = backend.list_approvals(WS_ID)
    assert len(result) == 2


@responses.activate
def test_submit_approval(backend):
    """submit_approval POSTs to the approvals endpoint."""
    appr = make_approval()
    responses.add(responses.POST, APPROVALS_URL, json=appr, status=201)
    result = backend.submit_approval(WS_ID, {
        "dateRangeStart": "2026-03-01T00:00:00Z",
        "dateRangeEnd": "2026-03-07T23:59:59Z",
    })
    assert result["id"] == appr["id"]


@responses.activate
def test_submit_approval_for_user(backend):
    """submit_approval_for_user POSTs to the user-specific endpoint."""
    appr = make_approval()
    url = f"{APPROVALS_URL}/users/{USER_ID}"
    responses.add(responses.POST, url, json=appr, status=201)
    result = backend.submit_approval_for_user(WS_ID, USER_ID, {
        "dateRangeStart": "2026-03-01T00:00:00Z",
        "dateRangeEnd": "2026-03-07T23:59:59Z",
    })
    assert result["status"] == "PENDING"


@responses.activate
def test_update_approval(backend):
    """update_approval PATCHes the approval."""
    appr = make_approval(status="APPROVED")
    url = f"{APPROVALS_URL}/{appr['id']}"
    responses.add(responses.PATCH, url, json=appr, status=200)
    result = backend.update_approval(WS_ID, appr["id"], {"status": "APPROVE"})
    assert result["status"] == "APPROVED"


@responses.activate
def test_approval_list_status_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, APPROVALS_URL,
        json=[make_approval(status="PENDING")],
        status=200,
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "approval", "list", "--status", "PENDING", "--json"])
    assert result.exit_code == 0, result.output
    assert "status=PENDING" in responses.calls[0].request.url


@responses.activate
def test_approval_list_sort_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, APPROVALS_URL,
        json=[make_approval()],
        status=200,
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "approval", "list", "--sort-column", "ID", "--sort-order", "ASCENDING", "--json"])
    assert result.exit_code == 0, result.output
    assert "sort-column=ID" in responses.calls[0].request.url
