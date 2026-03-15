# Clockify CLI — Test Plan & Results

## Summary

**289 tests · 27 files · ~0.5s runtime · all mocked (no network)**

All tests pass as of 2026-03-14 after the God Object refactor (monolithic `clockify_backend.py` → 16 domain mixins; monolithic `clockify_cli.py` → 17 command modules).

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

## Domain Coverage Table

| File | Tests | Covers |
|------|------:|--------|
| `test_parity_gaps.py` | 61 | Deep coverage of groups, webhooks, approval, time-off, scheduling, expenses, users, reports, invoices, misc |
| `test_cli_coverage.py` | 39 | Cross-domain coverage for commands missing from dedicated files |
| `test_cli_gaps_2.py` | 21 | Additional gap-fill: shared-reports, entities, entries bulk ops |
| `test_backend.py` | 18 | HTTP infrastructure: retry on 429, deep-merge, pagination, error mapping, dry-run, verbose |
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
| **Total** | **289** | |

## Known Gaps

- **No dedicated mixin unit tests** — `core/mixins/*.py` is covered indirectly through CLI tests. A failure in a mixin method will show up as a CLI test failure, but the mixin itself is not tested in isolation.
- **No REPL integration tests** — `_run_repl` is not tested; it's a prompt_toolkit loop that's hard to drive in unit tests.
- **No error path completeness** — 401, 403, 404, 429 retry, and 500 errors are tested in `test_backend.py` at the HTTP layer, but not exhaustively for every command.
- **`commands` manifest count** — `test_cli_coverage.py` asserts `len(data) > 50`, not an exact count. The actual count is 161 (as of 2026-03-14 after recursive walker fix).

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

## Results (2026-03-14)

```
289 passed, 77 warnings in 0.53s
```

Warnings are all `DeprecationWarning: Argument 'match_querystring' is deprecated` from the `responses` library — tests use `match_querystring=False` (legacy positional arg style). No functional impact.
