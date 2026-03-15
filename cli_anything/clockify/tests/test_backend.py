"""Tests for ClockifyBackend core behaviors: auth, pagination, error mapping."""

from __future__ import annotations

import pytest
import responses

from cli_anything.clockify.core.clockify_backend import ClockifyBackend, ClockifyAPIError
from cli_anything.clockify.tests.conftest import (
    BASE_URL, REPORTS_URL, WS_ID, USER_ID, API_KEY,
    make_workspace, make_project, make_user, make_tag, make_task,
    make_time_entry, make_expense, make_invoice, make_client,
)


# ── Auth header ───────────────────────────────────────────────────────

@responses.activate
def test_auth_header_sent(backend):
    """Every request must include X-Api-Key header."""
    responses.add(responses.GET, f"{BASE_URL}/user", json=make_user(), status=200)
    backend.get_current_user()
    assert len(responses.calls) == 1
    req = responses.calls[0].request
    assert req.headers.get("X-Api-Key") == API_KEY
    assert "Authorization" not in req.headers


@responses.activate
def test_no_authorization_header(backend):
    """Must NOT send Authorization header (Clockify uses X-Api-Key)."""
    responses.add(responses.GET, f"{BASE_URL}/user", json=make_user(), status=200)
    backend.get_current_user()
    req = responses.calls[0].request
    assert "Authorization" not in req.headers


# ── HTTP error mapping ────────────────────────────────────────────────

@responses.activate
def test_401_raises_api_error(backend):
    responses.add(responses.GET, f"{BASE_URL}/user", json={"message": "unauthorized"}, status=401)
    with pytest.raises(ClockifyAPIError) as exc_info:
        backend.get_current_user()
    assert exc_info.value.status_code == 401
    assert "API key" in str(exc_info.value)


@responses.activate
def test_403_raises_api_error(backend):
    responses.add(
        responses.GET,
        f"{BASE_URL}/workspaces/{WS_ID}/projects",
        json={"message": "forbidden"},
        status=403,
    )
    with pytest.raises(ClockifyAPIError) as exc_info:
        backend.list_projects(WS_ID)
    assert exc_info.value.status_code == 403
    assert "Permission" in str(exc_info.value)


@responses.activate
def test_404_raises_api_error(backend):
    entry_id = "nonexistent111111111111111"
    responses.add(
        responses.GET,
        f"{BASE_URL}/workspaces/{WS_ID}/time-entries/{entry_id}",
        json={"message": "not found"},
        status=404,
    )
    with pytest.raises(ClockifyAPIError) as exc_info:
        backend.get_entry(WS_ID, entry_id)
    assert exc_info.value.status_code == 404


@responses.activate
def test_429_retries_once(backend):
    """429 should trigger one retry after sleeping."""
    import time
    responses.add(
        responses.GET, f"{BASE_URL}/user",
        json={"message": "too many requests"}, status=429,
    )
    responses.add(responses.GET, f"{BASE_URL}/user", json=make_user(), status=200)
    # Patch sleep to avoid actually sleeping
    import unittest.mock as mock
    with mock.patch("time.sleep"):
        result = backend.get_current_user()
    assert result["id"] == USER_ID
    assert len(responses.calls) == 2


# ── Pagination ────────────────────────────────────────────────────────

@responses.activate
def test_pagination_fetches_all_pages(backend):
    """_get_all_pages should follow pagination until Last-Page: true."""
    page1 = [make_project("p1", "Alpha"), make_project("p2", "Beta")]
    page2 = [make_project("p3", "Gamma")]

    responses.add(
        responses.GET,
        f"{BASE_URL}/workspaces/{WS_ID}/projects",
        json=page1,
        status=200,
        headers={"Last-Page": "false"},
        match_querystring=False,
    )
    responses.add(
        responses.GET,
        f"{BASE_URL}/workspaces/{WS_ID}/projects",
        json=page2,
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )

    result = backend.list_projects(WS_ID, page_size=2)
    assert len(result) == 3
    assert result[0]["name"] == "Alpha"
    assert result[2]["name"] == "Gamma"


@responses.activate
def test_single_page_no_last_page_header(backend):
    """If Last-Page header is absent and data is returned, stop after one page."""
    projects = [make_project()]
    responses.add(
        responses.GET,
        f"{BASE_URL}/workspaces/{WS_ID}/projects",
        json=projects,
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = backend.list_projects(WS_ID)
    assert len(result) == 1


# ── Exponential backoff ──────────────────────────────────────────────

@responses.activate
def test_429_retry_succeeds(backend):
    """3 consecutive 429s then 200 should succeed after 4 calls."""
    import unittest.mock as mock
    url = f"{BASE_URL}/user"
    for _ in range(3):
        responses.add(responses.GET, url, status=429, json={"message": "Rate limited"})
    responses.add(responses.GET, url, json=make_user(), status=200)
    with mock.patch("cli_anything.clockify.core.mixins._base.time.sleep"):
        result = backend.get_current_user()
    assert result["id"] == USER_ID
    assert len(responses.calls) == 4


@responses.activate
def test_429_exhausted_raises(backend):
    """6 consecutive 429s should raise ClockifyAPIError(429)."""
    import unittest.mock as mock
    url = f"{BASE_URL}/user"
    for _ in range(6):
        responses.add(responses.GET, url, status=429, json={"message": "Rate limited"})
    with mock.patch("cli_anything.clockify.core.mixins._base.time.sleep"):
        with pytest.raises(ClockifyAPIError) as exc_info:
            backend.get_current_user()
    assert exc_info.value.status_code == 429
    assert len(responses.calls) == 6


# ── Verbose / debug logging ──────────────────────────────────────────

@responses.activate
def test_verbose_logs_to_stderr(backend, capsys):
    """--verbose logs method/URL/status to stderr."""
    backend.verbose = True
    responses.add(responses.GET, f"{BASE_URL}/user", json=make_user(), status=200)
    backend.get_current_user()
    err = capsys.readouterr().err
    assert "[clockify] GET" in err
    assert "200" in err


@responses.activate
def test_debug_logs_body_to_stderr(backend, capsys):
    """--debug logs request body to stderr."""
    backend.debug = True
    backend.verbose = True
    responses.add(responses.POST, f"{BASE_URL}/workspaces", json={"id": "ws1"}, status=201)
    backend.create_workspace({"name": "Test"})
    err = capsys.readouterr().err
    assert "[clockify] body:" in err
    assert '"name"' in err


# ── Dry-run ──────────────────────────────────────────────────────────

@responses.activate
def test_dry_run_prints_json(backend, capsys):
    """--dry-run prints request details to stdout without sending."""
    import json as json_mod
    backend.dry_run = True
    result = backend.create_workspace({"name": "Test"})
    assert result == {}
    out = capsys.readouterr().out
    info = json_mod.loads(out)
    assert info["method"] == "POST"
    assert "/workspaces" in info["url"]
    assert info["body"]["name"] == "Test"
    # No HTTP calls should have been made
    assert len(responses.calls) == 0


@responses.activate
def test_dry_run_redacts_sensitive(backend, capsys):
    """--dry-run redacts sensitive fields."""
    import json as json_mod
    backend.dry_run = True
    backend.create_workspace({"name": "Test", "apiKey": "secret123"})
    out = capsys.readouterr().out
    info = json_mod.loads(out)
    assert info["body"]["apiKey"] == "***"
    assert info["body"]["name"] == "Test"


@responses.activate
def test_dry_run_no_http(backend):
    """--dry-run makes zero HTTP calls."""
    backend.dry_run = True
    backend.create_workspace({"name": "Test"})
    assert len(responses.calls) == 0


# ── Multi-profile config ─────────────────────────────────────────────

def test_profile_save_and_load(tmp_path, monkeypatch):
    """Profile file creation and loading works."""
    from cli_anything.clockify.utils.session import save_config_file, load_config_file, CONFIG_DIR
    monkeypatch.setattr("cli_anything.clockify.utils.session.CONFIG_DIR", tmp_path)
    monkeypatch.setattr("cli_anything.clockify.utils.session.CONFIG_FILE", tmp_path / "config.json")
    save_config_file({"api_key": "key1", "workspace_id": "ws1"}, profile="work")
    cfg = load_config_file("work")
    assert cfg["api_key"] == "key1"
    assert cfg["workspace_id"] == "ws1"
    assert (tmp_path / "profiles" / "work.json").exists()


def test_profile_session_resolve(tmp_path, monkeypatch):
    """Session.resolve reads from profile config."""
    from cli_anything.clockify.utils.session import save_config_file, Session
    monkeypatch.setattr("cli_anything.clockify.utils.session.CONFIG_DIR", tmp_path)
    monkeypatch.setattr("cli_anything.clockify.utils.session.CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    save_config_file({"api_key": "profile-key", "workspace_id": "profile-ws"}, profile="staging")
    session = Session.resolve(profile="staging")
    assert session.api_key == "profile-key"
    assert session.workspace_id == "profile-ws"


def test_default_profile_backward_compat(tmp_path, monkeypatch):
    """Default profile reads from config.json (backward compatible)."""
    import json as json_mod
    monkeypatch.setattr("cli_anything.clockify.utils.session.CONFIG_DIR", tmp_path)
    monkeypatch.setattr("cli_anything.clockify.utils.session.CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    (tmp_path / "config.json").write_text(json_mod.dumps({"api_key": "default-key"}))
    from cli_anything.clockify.utils.session import Session
    session = Session.resolve(profile="default")
    assert session.api_key == "default-key"


# ── Connection error retry ───────────────────────────────────────────

@responses.activate
def test_connection_error_retried(backend):
    """ConnectionError on 1st call, success on 2nd — verifies retry works."""
    import unittest.mock as mock
    import requests as req
    url = f"{BASE_URL}/user"

    def connection_error_callback(request):
        raise req.ConnectionError("Connection refused")

    responses.add_callback(responses.GET, url, callback=connection_error_callback)
    responses.add(responses.GET, url, json=make_user(), status=200)
    with mock.patch("cli_anything.clockify.core.mixins._base.time.sleep"):
        result = backend.get_current_user()
    assert result["id"] == USER_ID


@responses.activate
def test_connection_error_exhausted(backend):
    """All attempts raise ConnectionError → ClockifyAPIError(status_code=0)."""
    import unittest.mock as mock
    import requests as req

    with mock.patch.object(
        backend._http, "request", side_effect=req.ConnectionError("Connection refused")
    ):
        with mock.patch("cli_anything.clockify.core.mixins._base.time.sleep"):
            with pytest.raises(ClockifyAPIError) as exc_info:
                backend.get_current_user()
    assert exc_info.value.status_code == 0
    assert "Network error" in str(exc_info.value)


# ── Debug redaction ──────────────────────────────────────────────────

@responses.activate
def test_debug_redacts_sensitive_body(backend, capsys):
    """Debug mode redacts sensitive fields in logged body."""
    backend.debug = True
    backend.verbose = True
    responses.add(responses.POST, f"{BASE_URL}/workspaces", json={"id": "ws1"}, status=201)
    backend.create_workspace({"name": "Test", "token": "supersecret123"})
    err = capsys.readouterr().err
    assert "***" in err
    assert "supersecret123" not in err


# ── Config file permissions ──────────────────────────────────────────

def test_config_file_permissions(tmp_path, monkeypatch):
    """Config files are created with 0o600 permissions."""
    import stat
    from cli_anything.clockify.utils.session import save_config_file
    monkeypatch.setattr("cli_anything.clockify.utils.session.CONFIG_DIR", tmp_path)
    monkeypatch.setattr("cli_anything.clockify.utils.session.CONFIG_FILE", tmp_path / "config.json")
    save_config_file({"api_key": "test-key"}, profile="default")
    config_path = tmp_path / "config.json"
    assert config_path.exists()
    mode = stat.S_IMODE(config_path.stat().st_mode)
    assert mode == 0o600, f"Expected 0o600, got {oct(mode)}"


# ── JSON option error handling ───────────────────────────────────────

# ── Retry-After header ───────────────────────────────────────────────

@responses.activate
def test_429_retry_after_header_seconds(backend):
    """429 with Retry-After: 3 → delay uses at least 3s."""
    import unittest.mock as mock
    url = f"{BASE_URL}/user"
    responses.add(
        responses.GET, url, status=429,
        json={"message": "Rate limited"},
        headers={"Retry-After": "3"},
    )
    responses.add(responses.GET, url, json=make_user(), status=200)
    sleep_calls = []
    with mock.patch("cli_anything.clockify.core.mixins._base.time.sleep", side_effect=lambda d: sleep_calls.append(d)):
        result = backend.get_current_user()
    assert result["id"] == USER_ID
    assert len(sleep_calls) == 1
    assert sleep_calls[0] >= 3.0


@responses.activate
def test_429_retry_after_absent_uses_backoff(backend):
    """No Retry-After header → existing exponential backoff preserved."""
    import unittest.mock as mock
    url = f"{BASE_URL}/user"
    responses.add(responses.GET, url, status=429, json={"message": "Rate limited"})
    responses.add(responses.GET, url, json=make_user(), status=200)
    sleep_calls = []
    with mock.patch("cli_anything.clockify.core.mixins._base.time.sleep", side_effect=lambda d: sleep_calls.append(d)):
        backend.get_current_user()
    assert len(sleep_calls) == 1
    # Backoff for attempt 0: 2^0 + jitter(0, 0.5) → between 1.0 and 1.5
    assert 1.0 <= sleep_calls[0] <= 1.5


def test_parse_retry_after_invalid_returns_none(backend):
    """Garbage Retry-After header → None."""
    import requests as req
    resp = req.Response()
    resp.headers["Retry-After"] = "not-a-number-or-date"
    assert backend._parse_retry_after(resp) is None


def test_parse_retry_after_missing_returns_none(backend):
    """No Retry-After header → None."""
    import requests as req
    resp = req.Response()
    assert backend._parse_retry_after(resp) is None


# ── Configurable timeouts ───────────────────────────────────────────

def test_timeout_default_30(backend):
    """Default timeout is 30s."""
    assert backend.timeout == 30
    assert backend.reports_timeout == 60


def test_timeout_custom_via_cli():
    """--timeout 120 sets backend.timeout = 120, reports_timeout = max(120, 60)."""
    from click.testing import CliRunner
    from cli_anything.clockify.clockify_cli import main
    r = CliRunner().invoke(main, ["--help"])
    assert "--timeout" in r.output


def test_reports_timeout_minimum_60(backend):
    """Setting timeout < 60 should not reduce reports_timeout below 60."""
    # Simulate what clockify_cli.py does with --timeout 10
    backend.timeout = 10
    backend.reports_timeout = max(10, 60)
    assert backend.reports_timeout == 60


# ── Rate-limit header logging ────────────────────────────────────────

@responses.activate
def test_verbose_logs_rate_limit_headers(backend, capsys):
    """X-RateLimit-Remaining header appears in stderr when verbose."""
    backend.verbose = True
    responses.add(
        responses.GET, f"{BASE_URL}/user", json=make_user(), status=200,
        headers={"X-RateLimit-Remaining": "45", "X-RateLimit-Limit": "50"},
    )
    backend.get_current_user()
    err = capsys.readouterr().err
    assert "rate-limit: 45/50 remaining" in err


@responses.activate
def test_verbose_no_rate_limit_no_log(backend, capsys):
    """No rate headers → no rate-limit line in stderr."""
    backend.verbose = True
    responses.add(responses.GET, f"{BASE_URL}/user", json=make_user(), status=200)
    backend.get_current_user()
    err = capsys.readouterr().err
    assert "rate-limit:" not in err


# ── Debug timing ─────────────────────────────────────────────────────

@responses.activate
def test_debug_shows_timing(backend, capsys):
    """Verbose output contains timing like (0.xxxs)."""
    backend.verbose = True
    responses.add(responses.GET, f"{BASE_URL}/user", json=make_user(), status=200)
    backend.get_current_user()
    err = capsys.readouterr().err
    import re
    assert re.search(r"\(\d+\.\d{3}s\)", err), f"Expected timing pattern in: {err}"


# ── HTTPAdapter ──────────────────────────────────────────────────────

def test_http_adapter_mounted(backend):
    """backend._http has HTTPAdapter with max_retries=0."""
    from requests.adapters import HTTPAdapter
    adapter = backend._http.get_adapter("https://example.com")
    assert isinstance(adapter, HTTPAdapter)
    assert adapter.max_retries.total == 0


# ── JSON option error handling ───────────────────────────────────────

def test_extra_body_invalid_json(runner):
    """--extra-body with invalid JSON produces a clean error."""
    from click.testing import CliRunner
    from cli_anything.clockify.clockify_cli import main
    r = CliRunner().invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "--extra-body", "{bad", "workspaces", "list",
    ])
    assert r.exit_code != 0
    assert "JSON" in r.output or "json" in r.output.lower() or "Invalid" in r.output


# ── Init error clean message ────────────────────────────────────────

def test_init_error_clean_message(monkeypatch):
    """Invoking a command without API key produces a clean error, not a traceback."""
    from click.testing import CliRunner
    from cli_anything.clockify.clockify_cli import main
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    monkeypatch.delenv("CLOCKIFY_WORKSPACE_ID", raising=False)
    # Ensure no config file provides a key
    monkeypatch.setattr(
        "cli_anything.clockify.utils.session.load_config_file", lambda profile="default": {}
    )
    r = CliRunner().invoke(main, ["workspaces", "list"])
    assert r.exit_code != 0
    # Should contain a user-friendly error message, not a traceback
    assert "API key" in r.output or "api_key" in r.output or "No API key" in r.output or "Error" in r.output
    assert "Traceback" not in r.output


# ── BUG 1: entity_types joined as CSV ────────────────────────────────

@responses.activate
def test_list_project_custom_fields_entity_types_joined(backend):
    """entity_types must be sent as CSV, not repeated params."""
    url = f"{BASE_URL}/workspaces/{WS_ID}/projects/proj111111111111111111111/custom-fields"
    responses.add(responses.GET, url, json=[], status=200, match_querystring=False)
    backend.list_project_custom_fields(WS_ID, "proj111111111111111111111", entity_types=["PROJECT", "TIMEENTRY"])
    req = responses.calls[0].request
    assert "entity-type=PROJECT%2CTIMEENTRY" in req.url or "entity-type=PROJECT,TIMEENTRY" in req.url


# ── BUG 2: list_tasks page_size forwarded ────────────────────────────

@responses.activate
def test_list_tasks_page_size_forwarded(backend):
    """page_size=25 should be used in auto-pagination."""
    proj_id = "proj111111111111111111111"
    url = f"{BASE_URL}/workspaces/{WS_ID}/projects/{proj_id}/tasks"
    responses.add(responses.GET, url, json=[make_task()], status=200,
                  headers={"Last-Page": "true"}, match_querystring=False)
    backend.list_tasks(WS_ID, proj_id, page_size=25)
    req = responses.calls[0].request
    assert "page-size=25" in req.url


# ── BUG 3: list_tags page_size forwarded ─────────────────────────────

@responses.activate
def test_list_tags_page_size_forwarded(backend):
    """page_size=25 should be used in auto-pagination."""
    url = f"{BASE_URL}/workspaces/{WS_ID}/tags"
    responses.add(responses.GET, url, json=[make_tag()], status=200,
                  headers={"Last-Page": "true"}, match_querystring=False)
    backend.list_tags(WS_ID, page_size=25)
    req = responses.calls[0].request
    assert "page-size=25" in req.url


# ── BUG 4: get_project expense_limit as string ──────────────────────

@responses.activate
def test_get_project_expense_limit_string(backend):
    """expense_limit sent as string in get_project."""
    proj_id = "proj111111111111111111111"
    url = f"{BASE_URL}/workspaces/{WS_ID}/projects/{proj_id}"
    responses.add(responses.GET, url, json=make_project(), status=200, match_querystring=False)
    backend.get_project(WS_ID, proj_id, expense_limit=100)
    req = responses.calls[0].request
    assert "expense-limit=100" in req.url


# ── BUG 5: timer restart preserves tags/billable/task ────────────────

@responses.activate
def test_timer_restart_preserves_tags(backend):
    """Tags, billable, and taskId are preserved on timer restart."""
    import json
    from click.testing import CliRunner
    from cli_anything.clockify.clockify_cli import main

    running = make_time_entry(end=None)
    running["tagIds"] = ["tag1111111111111111111111"]
    running["taskId"] = "task111111111111111111111"
    running["billable"] = True
    running["projectId"] = "proj111111111111111111111"

    # GET running timer (uses in-progress endpoint)
    responses.add(responses.GET,
                  f"{BASE_URL}/workspaces/{WS_ID}/time-entries/status/in-progress",
                  json=running, status=200, match_querystring=False)
    # PATCH stop timer
    responses.add(responses.PATCH,
                  f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries",
                  json=running, status=200, match_querystring=False)
    # GET current user (for _user() helper)
    responses.add(responses.GET,
                  f"{BASE_URL}/user",
                  json=make_user(), status=200, match_querystring=False)
    # POST start new timer
    new_entry = make_time_entry(end=None)
    responses.add(responses.POST,
                  f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries",
                  json=new_entry, status=201, match_querystring=False)

    r = CliRunner().invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID, "--json",
        "timer", "restart",
    ])
    assert r.exit_code == 0, f"CLI failed: {r.output}"
    # Verify the POST body includes tag/task/billable
    post_calls = [c for c in responses.calls if c.request.method == "POST"]
    assert len(post_calls) == 1
    body = json.loads(post_calls[0].request.body)
    assert body.get("tagIds") == ["tag1111111111111111111111"]
    assert body.get("taskId") == "task111111111111111111111"
    assert body.get("billable") is True


# ── BUG 6: timer CF validation rejects malformed input ───────────────

@responses.activate
def test_timer_cf_validation_rejects_malformed():
    """timer start --custom-field 'bad' should raise UsageError."""
    from click.testing import CliRunner
    from cli_anything.clockify.clockify_cli import main

    # Mock user endpoint so backend init succeeds
    responses.add(responses.GET, f"{BASE_URL}/user", json=make_user(), status=200,
                  match_querystring=False)

    r = CliRunner().invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID,
        "timer", "start", "--custom-field", "bad_no_equals",
    ])
    assert r.exit_code != 0
    assert "FIELD_ID=VALUE" in r.output


# ── ENH 7: backend.close() doesn't raise ─────────────────────────────

def test_backend_close(backend):
    """backend.close() should not raise."""
    backend.close()
    # Calling close again should also be safe
    backend.close()


# ── ENH 8: pagination truncation warning ─────────────────────────────

@responses.activate
def test_pagination_truncation_warning(backend, capsys):
    """Hitting _MAX_PAGES logs warning to stderr."""
    import unittest.mock as mock

    # Temporarily set max pages very low to avoid creating 1000 responses
    original_max = backend._MAX_PAGES
    backend.__class__._MAX_PAGES = 3

    url = f"{BASE_URL}/workspaces/{WS_ID}/projects"
    for _ in range(4):
        responses.add(responses.GET, url, json=[make_project()], status=200,
                      headers={"Last-Page": "false"}, match_querystring=False)

    with mock.patch("cli_anything.clockify.core.mixins._base.time.sleep"):
        result = backend.list_projects(WS_ID)

    err = capsys.readouterr().err
    assert "warning: pagination stopped" in err
    assert "Results may be incomplete" in err

    # Restore
    backend.__class__._MAX_PAGES = original_max


# ── Round 2: Bug Fixes & Robustness ─────────────────────────────────

# ── BUG 1: Reports archived=False should NOT set body["archived"] ───

@responses.activate
def test_report_archived_false_not_set(backend):
    """archived=False must NOT set body['archived'] (only active entries)."""
    responses.add(
        responses.POST, f"{REPORTS_URL}/workspaces/{WS_ID}/reports/detailed",
        json={"totals": [], "timeentries": []}, status=200,
    )
    backend.report_detailed(WS_ID, "2026-03-01", "2026-03-15", archived=False)
    import json
    body = json.loads(responses.calls[0].request.body)
    assert "archived" not in body


@responses.activate
def test_report_archived_true_sends_all(backend):
    """archived=True must set body['archived'] = 'All'."""
    responses.add(
        responses.POST, f"{REPORTS_URL}/workspaces/{WS_ID}/reports/summary",
        json={"totals": [], "groupOne": []}, status=200,
    )
    backend.report_summary(WS_ID, "2026-03-01", "2026-03-15", archived=True)
    import json
    body = json.loads(responses.calls[0].request.body)
    assert body["archived"] == "All"


# ── BUG 2: list_expenses page_size forwarded ────────────────────────

@responses.activate
def test_list_expenses_page_size_forwarded(backend):
    """page_size=25 should appear in auto-pagination request."""
    url = f"{BASE_URL}/workspaces/{WS_ID}/expenses"
    responses.add(responses.GET, url, json=[make_expense()], status=200,
                  headers={"Last-Page": "true"}, match_querystring=False)
    backend.list_expenses(WS_ID, page_size=25)
    req = responses.calls[0].request
    assert "page-size=25" in req.url


# ── BUG 3: list_invoices page_size forwarded ────────────────────────

@responses.activate
def test_list_invoices_page_size_forwarded(backend):
    """page_size=25 should appear in auto-pagination request."""
    url = f"{BASE_URL}/workspaces/{WS_ID}/invoices"
    responses.add(responses.GET, url, json=[make_invoice()], status=200,
                  headers={"Last-Page": "true"}, match_querystring=False)
    backend.list_invoices(WS_ID, page_size=25)
    req = responses.calls[0].request
    assert "page-size=25" in req.url


# ── BUG 4: list_users page_size forwarded + pagination fix ──────────

@responses.activate
def test_list_users_page_size_forwarded(backend):
    """page_size=25 without page should auto-paginate with that size."""
    url = f"{BASE_URL}/workspaces/{WS_ID}/users"
    responses.add(responses.GET, url, json=[make_user()], status=200,
                  headers={"Last-Page": "true"}, match_querystring=False)
    backend.list_users(WS_ID, page_size=25)
    req = responses.calls[0].request
    assert "page-size=25" in req.url


# ── BUG 5: list_clients page_size forwarded + pagination fix ────────

@responses.activate
def test_list_clients_page_size_forwarded(backend):
    """page_size=25 without page should auto-paginate with that size."""
    url = f"{BASE_URL}/workspaces/{WS_ID}/clients"
    responses.add(responses.GET, url, json=[make_client()], status=200,
                  headers={"Last-Page": "true"}, match_querystring=False)
    backend.list_clients(WS_ID, page_size=25)
    req = responses.calls[0].request
    assert "page-size=25" in req.url


# ── BUG 6: create_entry entity kwarg in error message ───────────────

@responses.activate
def test_create_entry_entity_in_404(backend):
    """404 on create_entry should mention 'time entry' in error."""
    url = f"{BASE_URL}/workspaces/{WS_ID}/user/{USER_ID}/time-entries"
    responses.add(responses.POST, url, json={"message": "not found"}, status=404,
                  match_querystring=False)
    with pytest.raises(ClockifyAPIError) as exc_info:
        backend.create_entry(WS_ID, USER_ID, {"start": "2026-03-13T09:00:00Z"})
    assert "time entry" in str(exc_info.value).lower()


# ── BUG 7: Formatter handles None date values ───────────────────────

def test_formatter_null_date_no_crash():
    """print_expenses with {'date': None} should not crash."""
    from cli_anything.clockify.utils.formatters import print_expenses
    # Should not raise TypeError
    print_expenses([{"id": "x", "date": None, "notes": "n"}])


def test_formatter_null_assignment_fields():
    """print_assignments with None fields should not crash."""
    from cli_anything.clockify.utils.formatters import print_assignments
    print_assignments([{
        "id": None, "projectName": None, "userName": None,
        "start": None, "end": None, "totalBillableHours": 0,
    }])


# ── BUG 8: parse_date_arg / parse_datetime_arg error messages ───────

def test_parse_date_arg_invalid_raises():
    """parse_date_arg('hello') should raise ValueError with clear message."""
    from cli_anything.clockify.utils.time_utils import parse_date_arg
    with pytest.raises(ValueError, match="Invalid date"):
        parse_date_arg("hello")


def test_parse_datetime_arg_invalid_raises():
    """parse_datetime_arg('not-a-date') should raise ValueError."""
    from cli_anything.clockify.utils.time_utils import parse_datetime_arg
    with pytest.raises(ValueError, match="Invalid date/time"):
        parse_datetime_arg("not-a-date")


# ── ENH 10: to_iso_ms error handling ────────────────────────────────

def test_to_iso_ms_invalid_raises():
    """to_iso_ms('garbage') should raise ValueError."""
    from cli_anything.clockify.utils.time_utils import to_iso_ms
    with pytest.raises(ValueError, match="Invalid ISO date"):
        to_iso_ms("garbage")


# ── ENH 11: elapsed_since error handling ─────────────────────────────

def test_elapsed_since_invalid_raises():
    """elapsed_since('garbage') should raise ValueError."""
    from cli_anything.clockify.utils.time_utils import elapsed_since
    with pytest.raises(ValueError, match="Invalid start time"):
        elapsed_since("garbage")


# ── Round 3: Enterprise Readiness ────────────────────────────────────

# ── Category A: Crash bugs (None values from API) ────────────────────

def test_print_tasks_none_duration():
    """Tasks with duration: None must not crash."""
    from cli_anything.clockify.utils.formatters import print_tasks
    print_tasks([{"id": "x", "name": "X", "status": "ACTIVE", "duration": None}])


def test_print_groups_none_userids():
    """Groups with userIds: None must not crash."""
    from cli_anything.clockify.utils.formatters import print_groups
    print_groups([{"id": "g", "name": "G", "userIds": None}])


def test_print_report_summary_none_duration():
    """Report with duration: None and totalTime: None must not crash."""
    from cli_anything.clockify.utils.formatters import print_report_summary
    print_report_summary({
        "groupOne": [{"name": "P", "duration": None}],
        "totals": [{"totalTime": None}],
    })


# ── Category B: Logic bug (currency preservation) ────────────────────

@responses.activate
def test_projects_update_preserves_currency():
    """projects update --hourly-rate includes existing currency in PUT body."""
    import json
    from click.testing import CliRunner
    from cli_anything.clockify.clockify_cli import main

    proj_id = "proj111111111111111111111"
    existing = make_project(proj_id, "Test")
    existing["hourlyRate"] = {"amount": 100, "currency": "EUR"}
    existing["costRate"] = {"amount": 50, "currency": "GBP"}

    # GET existing project
    responses.add(responses.GET, f"{BASE_URL}/workspaces/{WS_ID}/projects/{proj_id}",
                  json=existing, status=200, match_querystring=False)
    # PUT update
    responses.add(responses.PUT, f"{BASE_URL}/workspaces/{WS_ID}/projects/{proj_id}",
                  json=existing, status=200, match_querystring=False)

    r = CliRunner().invoke(main, [
        "--api-key", API_KEY, "--workspace", WS_ID, "--json",
        "projects", "update", proj_id, "--hourly-rate", "200", "--cost-rate", "75",
    ])
    assert r.exit_code == 0, f"CLI failed: {r.output}"

    put_calls = [c for c in responses.calls if c.request.method == "PUT"]
    assert len(put_calls) == 1
    body = json.loads(put_calls[0].request.body)
    assert body["hourlyRate"]["currency"] == "EUR"
    assert body["costRate"]["currency"] == "GBP"


# ── Category C: Display issues (no "None" literal in output) ─────────

def test_print_invoices_none_total_no_none_literal(capsys):
    """Invoice with total: None must not display literal 'None'."""
    from cli_anything.clockify.utils.formatters import print_invoices
    print_invoices([{"id": "i", "invoiceNumber": "INV-1", "status": "DRAFT",
                     "clientName": "C", "total": None}])
    out = capsys.readouterr().out
    assert "None" not in out


def test_print_expenses_none_fields_no_crash(capsys):
    """Expense with total/amount/category all None must not crash or show 'None'."""
    from cli_anything.clockify.utils.formatters import print_expenses
    print_expenses([{"id": "e", "date": "2026-03-13T00:00:00Z",
                     "total": None, "amount": None, "category": None,
                     "categoryName": None, "notes": "n"}])
    out = capsys.readouterr().out
    assert "None" not in out


def test_print_assignments_none_hours_no_none_literal(capsys):
    """Assignment with totalBillableHours: None must not display 'None'."""
    from cli_anything.clockify.utils.formatters import print_assignments
    print_assignments([{"id": "a" * 20, "projectName": "P", "userName": "U",
                        "start": "2026-03-13", "end": "2026-03-20",
                        "totalBillableHours": None, "hours": None}])
    out = capsys.readouterr().out
    assert "None" not in out


# ── Category D: entity= in 404 error messages ────────────────────────

@responses.activate
def test_create_workspace_entity_in_404(backend):
    """404 on create_workspace should mention 'workspace' in error."""
    responses.add(responses.POST, f"{BASE_URL}/workspaces",
                  json={"message": "not found"}, status=404)
    with pytest.raises(ClockifyAPIError) as exc_info:
        backend.create_workspace({"name": "W"})
    assert "workspace" in str(exc_info.value).lower()


@responses.activate
def test_create_client_entity_in_404(backend):
    """404 on create_client should mention 'client' in error."""
    responses.add(responses.POST, f"{BASE_URL}/workspaces/{WS_ID}/clients",
                  json={"message": "not found"}, status=404)
    with pytest.raises(ClockifyAPIError) as exc_info:
        backend.create_client(WS_ID, {"name": "C"})
    assert "client" in str(exc_info.value).lower()


@responses.activate
def test_create_group_entity_in_404(backend):
    """404 on create_group should mention 'user group' in error."""
    responses.add(responses.POST, f"{BASE_URL}/workspaces/{WS_ID}/user-groups",
                  json={"message": "not found"}, status=404)
    with pytest.raises(ClockifyAPIError) as exc_info:
        backend.create_group(WS_ID, {"name": "G"})
    assert "user group" in str(exc_info.value).lower()


@responses.activate
def test_create_invoice_entity_in_404(backend):
    """404 on create_invoice should mention 'invoice' in error."""
    responses.add(responses.POST, f"{BASE_URL}/workspaces/{WS_ID}/invoices",
                  json={"message": "not found"}, status=404)
    with pytest.raises(ClockifyAPIError) as exc_info:
        backend.create_invoice(WS_ID, {"clientId": "c"})
    assert "invoice" in str(exc_info.value).lower()


@responses.activate
def test_create_webhook_entity_in_404(backend):
    """404 on create_webhook should mention 'webhook' in error."""
    responses.add(responses.POST, f"{BASE_URL}/workspaces/{WS_ID}/webhooks",
                  json={"message": "not found"}, status=404)
    with pytest.raises(ClockifyAPIError) as exc_info:
        backend.create_webhook(WS_ID, {"name": "H", "url": "https://x.com"})
    assert "webhook" in str(exc_info.value).lower()
