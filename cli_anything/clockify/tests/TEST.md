# Clockify CLI — Test Plan & Results

## Summary

**380 tests · 28 files · ~4s runtime · all mocked (no network)**

All tests pass as of 2026-03-15 after Round 6 (Enterprise CLI Parity): enum corrections, required field enforcement, missing body field coverage, custom attributes, and comprehensive parity tests.

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
| `test_openapi_parity.py` | 1 | Spec-driven backend/OpenAPI operation parity against `openapi.cleaned 2.yaml` |
| `test_cli_coverage.py` | 56 | Cross-domain coverage: enum validations, MCP hardening, manifest assertion (exact 161 commands), parity tests for entries custom attributes, holidays/custom-fields required fields, entities optional dates, scheduling required params, users custom fields |
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
| `test_entities.py` | 5 | Entity created/updated/deleted audit, optional-dates backend test |
| **Total** | **380** | |

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

## Round 5 Changes (2026-03-15)

### OpenAPI Parity Fixes
- Entities endpoints: fixed query param name from `entityType` to `type` (spec-correct)
- Entities endpoints: fixed pagination param from `page-size` to `limit` (spec: 1-5000)
- Tasks create: added missing `contains-assignee` query parameter
- Users list: removed dead `--role` option (not in OpenAPI spec)
- Projects update: changed `--archived` from is_flag to `--archived/--no-archived` (allows un-archiving)
- Projects create/update: changed `--hourly-rate` and `--cost-rate` from float to int (spec: cents)
- Timer: added `page`/`page-size` support to `get_running_timer` per spec
- Shared reports: fixed `shared-reports get` to use `GET /v1/shared-reports/{id}` on the reports domain

### Bug Fixes
- `session.resolve_workspace`: handle zero workspaces with proper error message
- `session.resolve_user`: guard against missing `id` key in API response
- `time_utils.parse_duration_iso`: support days component (`P1DT2H` → 93600s)
- `_base._get_all_pages`: fix empty dict response causing unnecessary API calls

### Code Quality
- Added `entity=` kwargs to 9 backend methods (better error messages on 404)

## Known Gaps

- **No dedicated mixin unit tests** — `core/mixins/*.py` is covered indirectly through CLI tests.
- **No REPL integration tests** — `_run_repl` is a prompt_toolkit loop that's hard to drive in unit tests.
- **No 204 No Content explicit test** — tested indirectly via DELETE operations.
- **REPL connection pool leak** — each REPL command creates a new backend/session without closing the previous one. No impact on CLI mode.
- **REPL global flags not preserved** — `--json`/`--verbose`/`--debug` set at startup are overwritten per command.

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

## Round 6 Changes (2026-03-15)

### Enterprise CLI Parity (29 new tests)
- Fixed 5 enum correctness bugs in reports (approval-state, invoicing-state, amount-shown)
- Made scheduling batch-totals, capacity-filter, list, publish `--start`/`--end` required per spec
- Made holidays update `--name`, `--date`, `--recurring` required per spec (PUT = full replacement)
- Made custom-fields update `--name`, `--field-type` required per spec (PUT = full replacement)
- Added `--custom-attribute` to entries add/add-direct (spec: customAttributes array)
- Added `--custom-field` to users update-profile (spec: userCustomFields array)
- Enriched users filter from 3 to 12+ body fields
- Enriched users update-profile from 1 to 6+ body fields
- Made entities `--type` repeatable (spec: array query param)
- Made entities `--start`/`--end` optional (spec: defaults to 30-day range)

## Results (2026-03-15)

```
380 passed, 104 warnings in ~4s
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
