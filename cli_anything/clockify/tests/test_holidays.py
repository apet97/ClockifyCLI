"""Tests for holiday operations."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID,
)

HOLIDAYS_URL = f"{BASE_URL}/workspaces/{WS_ID}/holidays"


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


@responses.activate
def test_list_holidays(backend):
    """list_holidays returns list of holidays."""
    holidays = [make_holiday("h1", "New Year"), make_holiday("h2", "Christmas")]
    responses.add(responses.GET, HOLIDAYS_URL, json=holidays, status=200)
    result = backend.list_holidays(WS_ID)
    assert len(result) == 2
    assert result[0]["name"] == "New Year"


@responses.activate
def test_create_holiday(backend):
    """create_holiday POSTs to holidays URL."""
    holiday = make_holiday()
    responses.add(responses.POST, HOLIDAYS_URL, json=holiday, status=201)
    result = backend.create_holiday(WS_ID, {
        "name": "New Year",
        "date": "2026-01-01T00:00:00Z",
        "recurring": True,
    })
    assert result["id"] == holiday["id"]


@responses.activate
def test_list_holidays_in_period(backend):
    """list_holidays_in_period GETs to the in-period endpoint."""
    in_period_url = f"{HOLIDAYS_URL}/in-period"
    holidays = [make_holiday()]
    responses.add(
        responses.GET, in_period_url,
        json=holidays, status=200,
        match_querystring=False,
    )
    result = backend.list_holidays_in_period(
        WS_ID,
        "2026-01-01T00:00:00Z",
        "2026-12-31T23:59:59Z",
    )
    assert len(result) == 1
    req = responses.calls[0].request
    assert "start=" in req.url
    assert "end=" in req.url


@responses.activate
def test_delete_holiday(backend):
    """delete_holiday sends DELETE to correct URL."""
    holiday_id = "hol1111111111111111111111"
    responses.add(responses.DELETE, f"{HOLIDAYS_URL}/{holiday_id}", json={}, status=200)
    backend.delete_holiday(WS_ID, holiday_id)
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_cli_holidays_list_json(runner, session):
    """holidays list --json returns JSON array."""
    from cli_anything.clockify.clockify_cli import main
    import json

    holidays = [make_holiday()]
    responses.add(responses.GET, HOLIDAYS_URL, json=holidays, status=200)

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "holidays", "list", "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["name"] == "New Year"
