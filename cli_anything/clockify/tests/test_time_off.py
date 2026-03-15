"""Tests for time off operations."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, USER_ID, API_KEY,
)

POLICIES_URL = f"{BASE_URL}/workspaces/{WS_ID}/time-off/policies"
BALANCE_URL = f"{BASE_URL}/workspaces/{WS_ID}/time-off/balance/user/{USER_ID}"


def make_policy(
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


@responses.activate
def test_list_time_off_policies(backend):
    """list_time_off_policies returns list of policies."""
    policies = [make_policy("p1", "Annual"), make_policy("p2", "Sick")]
    responses.add(responses.GET, POLICIES_URL, json=policies, status=200)
    result = backend.list_time_off_policies(WS_ID)
    assert len(result) == 2
    assert result[0]["name"] == "Annual"


@responses.activate
def test_create_time_off_policy(backend):
    """create_time_off_policy POSTs to policies URL."""
    policy = make_policy()
    responses.add(responses.POST, POLICIES_URL, json=policy, status=201)
    result = backend.create_time_off_policy(WS_ID, {
        "name": "Annual Leave",
        "timeOffType": "VACATION",
    })
    assert result["id"] == policy["id"]


@responses.activate
def test_create_time_off_request(backend):
    """create_time_off_request POSTs to the policy requests endpoint."""
    policy = make_policy()
    request_data = {
        "id": "req1111111111111111111111",
        "policyId": policy["id"],
        "status": "PENDING",
    }
    url = f"{POLICIES_URL}/{policy['id']}/requests"
    responses.add(responses.POST, url, json=request_data, status=201)
    result = backend.create_time_off_request(WS_ID, policy["id"], {
        "start": "2026-04-01T00:00:00Z",
        "end": "2026-04-05T23:59:59Z",
    })
    assert result["status"] == "PENDING"


@responses.activate
def test_get_time_off_balance(backend):
    """get_time_off_balance GETs the user balance endpoint."""
    balance = {"userId": USER_ID, "totalBalance": 20, "usedBalance": 5}
    responses.add(responses.GET, BALANCE_URL, json=balance, status=200)
    result = backend.get_time_off_balance(WS_ID, USER_ID)
    assert result["totalBalance"] == 20


@responses.activate
def test_delete_time_off_policy(backend):
    """delete_time_off_policy sends DELETE."""
    policy_id = "pol1111111111111111111111"
    responses.add(responses.DELETE, f"{POLICIES_URL}/{policy_id}", json={}, status=200)
    backend.delete_time_off_policy(WS_ID, policy_id)
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_cli_time_off_policies_list_json(runner, session):
    """time-off policies list --json returns JSON array."""
    from cli_anything.clockify.clockify_cli import main
    import json

    policies = [make_policy()]
    responses.add(responses.GET, POLICIES_URL, json=policies, status=200)

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "time-off", "policies", "list", "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["name"] == "Annual Leave"


@responses.activate
def test_time_off_policies_list_name_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, POLICIES_URL,
        json=[make_policy()],
        status=200,
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "time-off", "policies", "list", "--name", "Annual", "--json"])
    assert result.exit_code == 0, result.output
    assert "name=Annual" in responses.calls[0].request.url


@responses.activate
def test_time_off_policies_list_status_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, POLICIES_URL,
        json=[make_policy()],
        status=200,
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "time-off", "policies", "list", "--status", "ACTIVE", "--json"])
    assert result.exit_code == 0, result.output
    assert "status=ACTIVE" in responses.calls[0].request.url
