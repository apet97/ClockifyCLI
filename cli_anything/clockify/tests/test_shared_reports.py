"""Tests for shared report operations."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID,
)

SHARED_REPORTS_URL = f"{BASE_URL}/workspaces/{WS_ID}/shared-reports"


def make_shared_report(
    report_id: str = "sr11111111111111111111111",
    name: str = "Monthly Report",
    public: bool = False,
) -> dict:
    return {
        "id": report_id,
        "name": name,
        "isPublic": public,
        "workspaceId": WS_ID,
    }


@responses.activate
def test_list_shared_reports(backend):
    """list_shared_reports returns list."""
    reports = [make_shared_report("r1", "Monthly"), make_shared_report("r2", "Weekly")]
    responses.add(responses.GET, SHARED_REPORTS_URL, json=reports, status=200)
    result = backend.list_shared_reports(WS_ID)
    assert len(result) == 2
    assert result[0]["name"] == "Monthly"


@responses.activate
def test_create_shared_report(backend):
    """create_shared_report POSTs to shared-reports URL."""
    report = make_shared_report()
    responses.add(responses.POST, SHARED_REPORTS_URL, json=report, status=201)
    result = backend.create_shared_report(WS_ID, {"name": "Monthly Report", "isPublic": False})
    assert result["id"] == report["id"]


@responses.activate
def test_update_shared_report(backend):
    """update_shared_report PUTs to the report endpoint."""
    report = make_shared_report(public=True)
    url = f"{SHARED_REPORTS_URL}/{report['id']}"
    responses.add(responses.PUT, url, json=report, status=200)
    result = backend.update_shared_report(WS_ID, report["id"], {"isPublic": True})
    assert result["isPublic"] is True


@responses.activate
def test_delete_shared_report(backend):
    """delete_shared_report sends DELETE to correct URL."""
    report_id = "sr11111111111111111111111"
    responses.add(responses.DELETE, f"{SHARED_REPORTS_URL}/{report_id}", json={}, status=200)
    backend.delete_shared_report(WS_ID, report_id)
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_cli_shared_reports_list_json(runner, session):
    """shared-reports list --json returns JSON array."""
    from cli_anything.clockify.clockify_cli import main
    import json

    reports = [make_shared_report()]
    responses.add(responses.GET, SHARED_REPORTS_URL, json=reports, status=200)

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "shared-reports", "list", "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["name"] == "Monthly Report"
