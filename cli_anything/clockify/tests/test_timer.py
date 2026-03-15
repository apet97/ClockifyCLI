"""Tests for timer operations: start, stop, get running."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, USER_ID, make_time_entry,
)


TIMER_URL = f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries"
IN_PROGRESS_URL = f"{BASE_URL}/workspaces/{WS_ID}/time-entries/status/in-progress"


@responses.activate
def test_start_timer_no_end_field(backend):
    """start_timer must POST with 'start' but NOT 'end'."""
    import json as jsonlib
    running = make_time_entry(end=None)
    running["timeInterval"]["end"] = None

    responses.add(responses.POST, TIMER_URL, json=running, status=201)

    result = backend.start_timer(WS_ID, USER_ID, description="Coding")
    assert result["id"] == running["id"]

    req = responses.calls[0].request
    body = jsonlib.loads(req.body)
    assert "start" in body
    assert "end" not in body


@responses.activate
def test_stop_timer_sends_patch_with_end(backend):
    """stop_timer must send PATCH with an 'end' timestamp."""
    import json as jsonlib
    stopped = make_time_entry()
    responses.add(responses.PATCH, TIMER_URL, json=stopped, status=200)

    backend.stop_timer(WS_ID, USER_ID)

    req = responses.calls[0].request
    body = jsonlib.loads(req.body)
    assert "end" in body
    # end should look like ISO 8601
    assert "T" in body["end"]
    assert body["end"].endswith("Z")


@responses.activate
def test_get_running_timer_returns_entry(backend):
    """get_running_timer should return the entry if timer is running."""
    running = make_time_entry(end=None)
    responses.add(
        responses.GET, IN_PROGRESS_URL,
        json=[running], status=200,
        match_querystring=False,
    )
    result = backend.get_running_timer(WS_ID, USER_ID)
    assert result is not None
    assert result["id"] == running["id"]


@responses.activate
def test_get_running_timer_returns_none_when_empty(backend):
    """get_running_timer should return None when no timer is running."""
    responses.add(
        responses.GET, IN_PROGRESS_URL,
        json=[], status=200,
        match_querystring=False,
    )
    result = backend.get_running_timer(WS_ID, USER_ID)
    assert result is None


@responses.activate
def test_get_running_timer_returns_none_on_404(backend):
    """get_running_timer should return None when API returns 404."""
    responses.add(
        responses.GET, IN_PROGRESS_URL,
        json={"message": "not found"}, status=404,
        match_querystring=False,
    )
    result = backend.get_running_timer(WS_ID, USER_ID)
    assert result is None
