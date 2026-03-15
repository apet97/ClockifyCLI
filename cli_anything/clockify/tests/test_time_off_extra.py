"""Tests for additional time-off operations."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import BASE_URL, WS_ID, USER_ID

TIME_OFF_URL = f"{BASE_URL}/workspaces/{WS_ID}/time-off"
POLICY_ID = "pol1111111111111111111111"
REQUEST_ID = "req1111111111111111111111"


@responses.activate
def test_delete_time_off_request(backend):
    """delete_time_off_request sends DELETE to policy requests endpoint."""
    url = f"{TIME_OFF_URL}/policies/{POLICY_ID}/requests/{REQUEST_ID}"
    responses.add(responses.DELETE, url, json={}, status=200)
    result = backend.delete_time_off_request(WS_ID, POLICY_ID, REQUEST_ID)
    assert isinstance(result, dict)
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_update_time_off_request_status(backend):
    """update_time_off_request_status PATCHes the request."""
    url = f"{TIME_OFF_URL}/policies/{POLICY_ID}/requests/{REQUEST_ID}"
    payload = {"id": REQUEST_ID, "status": "APPROVED"}
    responses.add(responses.PATCH, url, json=payload, status=200)
    result = backend.update_time_off_request_status(
        WS_ID, POLICY_ID, REQUEST_ID, {"status": "APPROVED"}
    )
    assert result["id"] == REQUEST_ID
    assert result["status"] == "APPROVED"


@responses.activate
def test_create_time_off_request_for_user(backend):
    """create_time_off_request_for_user POSTs to user-specific endpoint."""
    url = f"{TIME_OFF_URL}/policies/{POLICY_ID}/users/{USER_ID}/requests"
    payload = {"id": REQUEST_ID}
    responses.add(responses.POST, url, json=payload, status=201)
    result = backend.create_time_off_request_for_user(
        WS_ID, POLICY_ID, USER_ID,
        {"start": "2026-04-01T00:00:00Z", "end": "2026-04-05T23:59:59Z"},
    )
    assert result["id"] == REQUEST_ID


@responses.activate
def test_list_workspace_time_off_requests(backend):
    """list_workspace_time_off_requests POSTs to requests endpoint."""
    url = f"{TIME_OFF_URL}/requests"
    requests_data = [
        {"id": "req1111111111111111111111", "status": "PENDING"},
        {"id": "req2222222222222222222222", "status": "APPROVED"},
    ]
    responses.add(responses.POST, url, json=requests_data, status=200)
    result = backend.list_workspace_time_off_requests(WS_ID, {})
    assert len(result) == 2


@responses.activate
def test_get_policy_balance(backend):
    """get_policy_balance GETs balance for a policy."""
    url = f"{TIME_OFF_URL}/balance/policy/{POLICY_ID}"
    payload = {"policyId": POLICY_ID, "balance": 10.0}
    responses.add(responses.GET, url, json=payload, status=200)
    result = backend.get_policy_balance(WS_ID, POLICY_ID)
    assert result["policyId"] == POLICY_ID
    assert result["balance"] == 10.0
