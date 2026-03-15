# Clockify CLI — Developer Guide

Full developer reference for `cli-anything-clockify`, a Clockify REST API CLI built on the CLI-Anything framework.

## What This Is

A Python CLI package that wraps the Clockify REST API. It uses Click for command dispatch, a mixin-based backend class for HTTP operations, and a prompt_toolkit REPL for interactive use. The package is installed as `clockify` (entry point) and is designed to be both human-friendly (colored output, interactive REPL) and agent-friendly (`--json` flag, structured manifest).

## Project Structure

```
cli_anything/clockify/
├── __init__.py                   # Re-exports main from clockify_cli.py
├── clockify_cli.py               # Thin root: main group, REPL, add_command calls, commands manifest
│
├── commands/                     # One module per CLI domain group
│   ├── __init__.py
│   ├── _helpers.py               # Shared: _ws, _user, _out, handle_errors, set_repl_mode, _parse_custom_fields
│   ├── approval.py               # clockify approval ...
│   ├── clients.py                # clockify clients ...
│   ├── entries.py                # clockify entries ...
│   ├── expenses.py               # clockify expenses ... (incl. categories sub-group)
│   ├── invoices.py               # clockify invoices ... (incl. payments sub-group)
│   ├── misc.py                   # groups, holidays, custom-fields, entities, config
│   ├── projects.py               # clockify projects ...
│   ├── reports.py                # clockify reports ...
│   ├── scheduling.py             # clockify scheduling ... (incl. assignments sub-group)
│   ├── shared_reports.py         # clockify shared-reports ...
│   ├── tags.py                   # clockify tags ...
│   ├── tasks.py                  # clockify tasks ...
│   ├── time_off.py               # clockify time-off ... (incl. policies/balance/request sub-groups)
│   ├── timer.py                  # clockify timer ...
│   ├── users.py                  # clockify users ...
│   └── workspaces.py             # clockify workspaces ...
│
├── core/
│   ├── clockify_backend.py       # Thin facade: inherits all 16 mixins + re-exports ClockifyAPIError
│   └── mixins/
│       ├── __init__.py
│       ├── _base.py              # HTTP infrastructure: _BackendBase, ClockifyAPIError, 14 private helpers
│       ├── _approval.py          # approval_list, submit_approval, ...
│       ├── _catalog.py           # clients, tags (shared catalog entities)
│       ├── _entries.py           # list_time_entries, create_time_entry, ...
│       ├── _expenses.py          # expenses + expense categories
│       ├── _invoices.py          # invoices + payments
│       ├── _misc.py              # groups, holidays, custom_fields, entities
│       ├── _projects.py          # projects + tasks (nested under project)
│       ├── _reports.py           # detailed/summary/weekly/attendance/expense reports
│       ├── _scheduling.py        # scheduling assignments
│       ├── _shared_reports.py    # shared report management
│       ├── _tasks.py             # tasks mixin (project-scoped tasks)
│       ├── _time_off.py          # time-off policies, requests, balance
│       ├── _timer.py             # start/stop/status timer
│       ├── _users.py             # user profile, status, cost/hourly rates
│       ├── _webhooks.py          # webhooks CRUD + logs + token regen
│       └── _workspaces.py        # workspace CRUD + invite + rates
│
└── utils/
    ├── formatters.py             # Human-readable output functions (fmt.*)
    ├── repl_skin.py              # REPL UI: banner, prompt, colors, completions
    ├── session.py                # Session dataclass + save_config_file + resolve()
    └── time_utils.py             # Date/time parsing helpers for CLI args

tests/
├── conftest.py                   # Fixtures: session, backend, runner; data factories (make_*)
├── TEST.md                       # Test plan + results
└── test_*.py                     # 27 test files, 349 tests total
```

## Architecture

### Mixin Pattern

`ClockifyBackend` (in `core/clockify_backend.py`) inherits from all 16 domain mixins plus `_BackendBase`:

```python
class ClockifyBackend(
    _TimerMixin, _EntriesMixin, _ProjectsMixin, ..., _BackendBase
):
    pass
```

Each mixin only calls `self._get / _post / _put / _patch / _delete / _get_all_pages / _reports_post` — all defined in `_BackendBase`. Mixins never import from each other.

### Command Module Pattern

Each `commands/<domain>.py` defines a `@click.group()` and imports it from nothing in `clockify_cli.py`. The file structure is:

```python
# commands/projects.py
import click
from ._helpers import _ws, _user, _out, handle_errors

@click.group()
def projects():
    """Manage projects."""

@projects.command("list")
@click.option(...)
@click.pass_context
@handle_errors
def projects_list(ctx, ...):
    ws = _ws(ctx)
    data = ctx.obj["backend"].list_projects(ws, ...)
    _out(ctx, data, fmt.format_projects)
```

`clockify_cli.py` then does:
```python
from cli_anything.clockify.commands.projects import projects
main.add_command(projects)
```

## How to Add a New API Endpoint

**1. Add method to the appropriate mixin** (`core/mixins/<domain>.py`):
```python
def get_thing(self, workspace_id: str, thing_id: str) -> dict:
    return self._get(
        f"/workspaces/{workspace_id}/things/{thing_id}",
        entity=f"thing {thing_id}",
    )
```

**2. Add CLI command** (`commands/<domain>.py`):
```python
@things.command("get")
@click.argument("thing_id")
@click.pass_context
@handle_errors
def things_get(ctx, thing_id):
    """Get a thing by ID."""
    ws = _ws(ctx)
    data = ctx.obj["backend"].get_thing(ws, thing_id)
    _out(ctx, data, fmt.format_thing)
```

**3. Write a test** (`tests/test_things.py`):
```python
import responses as resp
from click.testing import CliRunner
from cli_anything.clockify.clockify_cli import main
from .conftest import WS_ID, API_KEY, BASE_URL

@resp.activate
def test_things_get():
    resp.add(resp.GET, f"{BASE_URL}/workspaces/{WS_ID}/things/abc",
             json={"id": "abc", "name": "Foo"}, match_querystring=False)
    r = CliRunner().invoke(main, ["--api-key", API_KEY,
                                  "--workspace", WS_ID,
                                  "--json", "things", "get", "abc"])
    assert r.exit_code == 0
```

## Backend Conventions

All HTTP helpers live in `_BackendBase` (`core/mixins/_base.py`):

| Method | Notes |
|--------|-------|
| `_get(path, params, entity)` | GET request |
| `_post(path, data, entity)` | POST with JSON body |
| `_put(path, data, entity)` | PUT with JSON body |
| `_patch(path, data, entity)` | PATCH with JSON body |
| `_delete(path, entity)` | DELETE |
| `_get_all_pages(path, params, page_size, entity)` | Paginates automatically; stops when `Last-Page: true` header seen |
| `_reports_post(path, body)` | POST to `reports_url` (separate API domain) |

- `entity=` kwarg is used for the 404 error message: `"Not found: {entity}"` — **always set this** on new methods
- All non-2xx responses are converted to `ClockifyAPIError` with extracted message (400, 409, 422, etc.)
- Malformed JSON on 200 responses raises `ClockifyAPIError` (not raw `JSONDecodeError`)
- 429 responses are retried automatically with exponential backoff (up to 5 retries, base 2^n + jitter)
- `self.extra_body` is deep-merged into every JSON request body when set
- `self.dry_run = True` prints the request as JSON and returns `{}` without sending
- `self.verbose = True` logs `METHOD URL -> STATUS` to stderr
- `self.debug = True` also logs the request body (sensitive fields redacted)

## CLI Command Conventions

### Decorator Order

Every command uses this exact decorator order:
```python
@group.command("name")
@click.option(...)           # all options first
@click.argument(...)         # then arguments
@click.pass_context          # then pass_context
@handle_errors               # outermost (wraps everything)
def cmd_name(ctx, ...):
```

`handle_errors` is the outermost decorator (applied last), so it wraps the Click machinery. It finds `ctx` by scanning `args` for `isinstance(a, click.Context)`.

### Group Definition

Use `@click.group()` — **not** `@main.group()`. Groups are defined standalone in their own module and attached in `clockify_cli.py` via `main.add_command(group)`.

### Context Helpers

```python
ws = _ws(ctx)          # workspace ID (auto-resolves if not set; cached after first call)
uid = _user(ctx)       # current user ID (fetches from API on first call; cached)
_out(ctx, data, fmt.format_fn)   # JSON or human output dispatch
```

Never access `ctx.obj["backend"]` without checking for `init_error` first if the command might run during failed initialization.

## Session + Workspace Resolution

`Session.resolve()` picks up credentials in this priority order:
1. CLI flag (`--api-key`, `--workspace`, etc.)
2. Environment variable (`CLOCKIFY_API_KEY`, `CLOCKIFY_WORKSPACE_ID`, etc.)
3. Config file (`~/.config/clockify-cli/config.json` or `profiles/<name>.json`)
4. Raises `ValueError` if API key not found

`_ws(ctx)` calls `session.resolve_workspace(backend)`:
- If `workspace_id` is set → returns it immediately
- If zero workspaces → raises `ValueError` with guidance to create one
- If exactly 1 workspace → uses it, caches in `session.workspace_id`
- If multiple → raises `ValueError` listing all options

When `Session.resolve()` raises (e.g., no API key), `main()` catches it and stores:
```python
ctx.obj["init_error"] = str(e)
ctx.obj["backend"] = None
ctx.obj["session"] = None
```
Commands that call `_ws(ctx)` will then get a `AttributeError` on `None.resolve_workspace`. Commands that don't need auth (like `config`, `workspaces use`) check `init_error` and handle it.

## Configuration System

| Source | Mechanism |
|--------|-----------|
| CLI flag | `--api-key`, `--workspace`, `--base-url`, `--reports-url`, `--profile` |
| Env var | `CLOCKIFY_API_KEY`, `CLOCKIFY_WORKSPACE_ID`, `CLOCKIFY_BASE_URL`, `CLOCKIFY_REPORTS_URL`, `CLOCKIFY_PROFILE` |
| Config file | `~/.config/clockify-cli/config.json` (default profile) |
| Profile file | `~/.config/clockify-cli/profiles/<name>.json` |

Create/update a profile:
```bash
clockify config set-profile work --api-key <key> --workspace <id>
clockify --profile work entries today
```

## Output Conventions

All commands use `_out(ctx, data, human_fn)`:

```python
def _out(ctx, data, human_fn=None):
    if ctx.obj.get("json"):
        fmt.print_json(data)      # JSON mode (--json flag on root group)
    elif human_fn:
        human_fn(data)            # call formatter from utils/formatters.py
    else:
        fmt.print_json(data)      # fallback to JSON if no human fn provided
```

Formatter functions live in `utils/formatters.py` and are imported as `fmt`:
```python
from cli_anything.clockify.utils import formatters as fmt
```

## REPL Mode

When `clockify` is invoked with no subcommand, `_run_repl(ctx)` is called:
1. `set_repl_mode(True)` — disables `sys.exit(1)` in `handle_errors` (errors are displayed but don't exit)
2. Creates a prompt_toolkit session with tab completions
3. Loops reading lines, splitting with `shlex.split()`, and passing to `main.main(...)`
4. `set_repl_mode(False)` on exit

`_repl_mode` is a module-level bool in `commands/_helpers.py`, mutated by `set_repl_mode()` from `clockify_cli.py`.

## Test Patterns

Tests use the `responses` library to mock HTTP calls. Key rules:

**Always use `match_querystring=False`** on GET stubs when the command passes optional query params:
```python
resp.add(resp.GET, f"{BASE_URL}/workspaces/{WS_ID}/projects",
         json=[make_project()], match_querystring=False)
```

**Test IDs must be 25+ chars OR contain non-hex chars** to bypass `_resolve_project_id` name lookup:
```python
# This is treated as a direct ID (25 hex chars):
WS_ID = "ws111111111111111111111111"  # ✓ 26 chars

# This would trigger a name lookup (too short or non-hex):
project_id = "abc123"  # ✗ only 6 chars → treated as name, tries API call
```

**conftest.py provides**: `session`, `backend`, `runner` fixtures + `make_*` data factories for all entity types.

**Standard test structure**:
```python
import responses as resp
from click.testing import CliRunner
from cli_anything.clockify.clockify_cli import main
from .conftest import WS_ID, API_KEY, BASE_URL, make_project

@resp.activate
def test_projects_list():
    resp.add(resp.GET, f"{BASE_URL}/workspaces/{WS_ID}/projects",
             json=[make_project()], match_querystring=False)
    r = CliRunner().invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID,
                                  "--json", "projects", "list"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert len(data) == 1
```

## Enum Gotcha

Clockify enum values often differ from intuition. **Always grep the OpenAPI spec** before using an enum:

```bash
grep -i "hourly" /Users/15x/Downloads/anyCLI/openapi.cleaned.yaml
# → HOURLYRATE   (not HOURLY_RATE)
# → TIMEENTRY    (not TIME_ENTRY)
```

The spec lives at `/Users/15x/Downloads/anyCLI/openapi.cleaned.yaml`.

## Running Tests

```bash
cd /Users/15x/Downloads/anyCLI/CLI-Anything/clockify/agent-harness

# All tests (fast, <1s)
.venv/bin/pytest cli_anything/clockify/tests/ -q --tb=short

# Single domain
.venv/bin/pytest cli_anything/clockify/tests/test_projects.py -v

# Single test
.venv/bin/pytest cli_anything/clockify/tests/test_projects.py::test_projects_list -v
```

All 349 tests run in ~1s (no network calls — all HTTP is mocked).

## Entry Point

In `pyproject.toml`:
```toml
[project.scripts]
clockify = "cli_anything.clockify:main"
```

`cli_anything/clockify/__init__.py` re-exports `main` from `clockify_cli.py`:
```python
from cli_anything.clockify.clockify_cli import main
__all__ = ["main"]
```

## Commands Manifest

`clockify commands --json` returns a JSON array of all CLI commands, useful for agents:
```bash
clockify commands --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d))"
# → 161
```

Each entry: `{"name": "list", "group": "projects", "options": ["name", "archived", ...]}`.
Nested groups use slash notation: `"group": "invoices/payments"`, `"group": "time-off/policies"`.
