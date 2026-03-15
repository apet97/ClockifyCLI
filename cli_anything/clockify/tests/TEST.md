# Clockify CLI — Test Plan & Results

## Summary

**349 tests · 27 files · ~1s runtime · all mocked (no network)**

All tests pass as of 2026-03-15 after Round 4 (Code Quality & Enterprise Hardening): response handling hardening, input validation, file I/O safety checks, and 6 new tests.

## Test Strategy

**All tests** — no live Clockify API, no network. HTTP is intercepted by the `responses` library. Tests run in isolation in any environment with only `pip install -e ".[dev]"`.

**Two test levels:**
1. **CLI integration** — invoke the root `main` group via `click.testing.CliRunner`, stub HTTP with `@responses.activate`. Verifies the full stack: Click dispatch → command handler → backend method → HTTP request → response parsing → output.
2. **Backend unit** — instantiate `ClockifyBackend` directly, stub HTTP, call backend methods. Verifies HTTP behavior, pagination, error mapping.

**No dedicated mixin unit tests** — mixins are thin wrappers; coverage is achieved through CLI integration tests that exercise them.

## Key Conventions

- `match_querystring=False` on all GET stubs — commands pass optional query params that vary per call
- Test IDs use 25+ chars or non-hex chars to bypass `_resolve_project_id` name lookup (e.g., `WS_ID = "ws111111111111111111111111"`)
- `conftest.py` provides `session`, `backend`, `runner` fixtures and `make_*` factories
- `--api-key` and `--workspace` passed explicitly on every CLI invocation (no env leak between tests)
- All tests that invoke CLI commands use `@responses.activate` even if Click validates choices before HTTP (safety net)

## Domain Coverage Table

| File | Tests | Covers |
|------|------:|--------|
| `test_backend.py` | 80 | HTTP infrastructure: retry on 429/ConnectionError, pagination, error mapping (401-500+), dry-run, verbose, debug redaction, Retry-After, timeouts, rate-limit logging, profiles, config permissions, malformed JSON, 400/409 clean errors, empty custom field ID, file-not-found upload, bad export path |
| `test_parity_gaps.py` | 61 | Deep coverage of groups, webhooks, approval, time-off, scheduling, expenses, users, reports, invoices, misc |
| `test_cli_coverage.py` | 39 | Cross-domain coverage: enum validations, MCP hardening, manifest assertion (exact 161 commands) |
| `test_cli_gaps_2.py` | 21 | Additional gap-fill: shared-reports, entities, entries bulk ops |
| `test_invoices.py` | 9 | Invoice CRUD, duplicate, export, status, filter, settings |
| `test_entries.py` | 9 | Time entry list, get, add, update, delete, today |
| `test_projects.py` | 9 | Project list, get, create, update, delete, estimate, members |
| `test_scheduling.py` | 9 | Assignment list, create, update, delete, publish, totals |
| `test_time_off.py` | 8 | Policy list/create/update/delete, balance, request |
| `test_groups.py` | 8 | Group list, get, create, update, delete, add/remove user |
| `test_expenses.py` | 8 | Expense list, get, create, update, delete, category CRUD |
| `test_cli_gaps.py` | 8 | CLI-level gap fill across domains |
| `test_users.py` | 7 | User list, me, profile, update-status, cost-rate, hourly-rate |
| `test_webhooks.py` | 7 | Webhook list, get, create, update, delete, logs, regen-token |
| `test_tasks.py` | 6 | Task list, get, create, update, delete, cost-rate |
| `test_tags.py` | 6 | Tag list, get, create, update, delete |
| `test_clients.py` | 6 | Client list, get, create, update, delete |
| `test_approval.py` | 6 | Approval list, submit, resubmit, update |
| `test_custom_fields.py` | 6 | Custom field list, create, update, delete, project-fields |
| `test_timer.py` | 5 | Timer start, stop, status, restart |
| `test_time_off_extra.py` | 5 | Time-off edge cases: get policy, update policy, balance get |
| `test_reports.py` | 5 | Detailed, summary, weekly, attendance, expense reports |
| `test_shared_reports.py` | 5 | Shared report list, get, create, update, delete |
| `test_holidays.py` | 5 | Holiday list, in-period, create, update, delete |
| `test_entries_extra.py` | 5 | Entry edge cases: duplicate, bulk-delete, mark-invoiced |
| `test_workspaces.py` | 4 | Workspace list, use, invite, create |
| `test_entities.py` | 4 | Entity created/updated/deleted audit |
| **Total** | **349** | |

## Round 4 Changes (2026-03-15)

### New Tests Added (6)
- `test_malformed_json_response_raises` — 200 with non-JSON body raises `ClockifyAPIError`
- `test_400_raises_api_error_with_message` — 400 response produces clean error with API message
- `test_custom_field_empty_id_rejected` — `--custom-field =value` rejected with "empty" error
- `test_upload_photo_file_not_found` — nonexistent photo path produces "not found" error
- `test_409_raises_api_error` — 409 Conflict produces `ClockifyAPIError(409)` with message
- `test_invoice_export_bad_output_path` — export to nonexistent directory produces "directory" error

### Test Hardening
- Added `@responses.activate` to 9 tests that were missing it (7 enum + 2 backend tests)
- Changed manifest assertion from `>= 161` to exact `== 161`

## Known Gaps

- **No dedicated mixin unit tests** — `core/mixins/*.py` is covered indirectly through CLI tests.
- **No REPL integration tests** — `_run_repl` is a prompt_toolkit loop that's hard to drive in unit tests.
- **No 204 No Content explicit test** — tested indirectly via DELETE operations.

## Running Tests

```bash
cd /Users/15x/Downloads/anyCLI/CLI-Anything/clockify/agent-harness

# All tests
.venv/bin/pytest cli_anything/clockify/tests/ -q --tb=short

# Single domain
.venv/bin/pytest cli_anything/clockify/tests/test_projects.py -v

# Verbose with output
.venv/bin/pytest cli_anything/clockify/tests/ -v -s
```

## Results (2026-03-15)

```
349 passed, 99 warnings in ~1s
```

Warnings are all `DeprecationWarning: Argument 'match_querystring' is deprecated` from the `responses` library — tests use `match_querystring=False` (legacy positional arg style). No functional impact.

## Security Audit (2026-03-15)

Full audit passed:
- No hardcoded secrets/API keys in source code
- No `verify=False`, `eval()`, `exec()`, `subprocess` in source code
- No tracked sensitive files (`.env`, `.pem`, `.key`)
- All dependencies are well-known, mature packages
- API key transmitted via `X-Api-Key` header only (never `Authorization`)
- Config files created with `0o600` permissions
- Sensitive fields redacted in debug/dry-run output
