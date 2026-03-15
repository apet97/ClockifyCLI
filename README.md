# clockify-cli

A command-line interface for [Clockify](https://clockify.me) — control your time tracking from the terminal.

## Install

```bash
pip install -e ".[dev]"
```

## Setup

Get your API key from **Clockify → Profile Settings → API**.

```bash
export CLOCKIFY_API_KEY=your_api_key_here
export CLOCKIFY_WORKSPACE_ID=your_workspace_id   # optional, auto-resolved if you only have one
```

Or save it to a profile:

```bash
clockify config set-profile work --api-key <key> --workspace <id>
clockify --profile work entries today
```

### Regional endpoints

```bash
export CLOCKIFY_BASE_URL=https://euc1.clockify.me/api/v1
export CLOCKIFY_REPORTS_URL=https://euc1.clockify.me/report/v1
```

## Usage

```bash
# Timer
clockify timer start --description "Deep work" --project "My Project"
clockify timer status
clockify timer stop

# Entries
clockify entries today --json
clockify entries list --start 2026-03-01 --end 2026-03-31
clockify entries add --start 09:00 --end 10:30 --description "Meeting"

# Reports
clockify reports summary --start 2026-03-01 --end 2026-03-31
clockify reports detailed --start 2026-03-01 --end 2026-03-31 --json
```

## Flags

| Flag | Description |
|------|-------------|
| `--json` | Machine-readable JSON output. Destructive commands skip confirmation in JSON mode. |
| `--verbose` / `-v` | Log HTTP method, URL, and status to stderr. |
| `--debug` | Log HTTP calls plus request body to stderr. |
| `--dry-run` | Print the request without sending it. Sensitive fields are redacted. |
| `--profile NAME` | Use a named credential profile (`CLOCKIFY_PROFILE` env var). |
| `--api-key KEY` | API key (overrides env/config). |
| `--workspace ID` | Workspace ID (overrides env/config). |

```bash
clockify --dry-run entries add --start 09:00 --end 10:00
# → {"method": "POST", "url": "...", "body": {...}}  (no request sent)

clockify --verbose entries today
# stderr: [clockify] GET https://api.clockify.me/api/v1/... -> 200
```

Rate-limited responses (429) are retried automatically with exponential backoff — up to 5 retries.

## Commands

### `timer`

```
clockify timer start    [--description TEXT] [--project NAME_OR_ID] [--tag TAG_ID] [--at HH:MM]
clockify timer stop
clockify timer status
clockify timer restart
```

### `entries`

```
clockify entries list          [--start DATE] [--end DATE] [--project ID] [--task ID]
                                [--description TEXT] [--in-progress] [--page N] [--page-size N]
clockify entries today
clockify entries get           <entry_id>
clockify entries add           --start HH:MM --end HH:MM [--description TEXT] [--project ID]
                                [--tag TAG_ID] [--task ID] [--billable] [--type REGULAR|BREAK]
clockify entries add-direct    --start HH:MM --end HH:MM  (workspace-scoped)
clockify entries update        <entry_id> [--description TEXT] [--start HH:MM] [--end HH:MM]
clockify entries delete        <entry_id> [--confirm]
clockify entries duplicate     <entry_id>
clockify entries bulk-delete   --ids <id,...>
clockify entries bulk-update   --ids <id,...> [--project ID] [--billable] [--tag TAG_ID]
clockify entries mark-invoiced --ids <id,...> [--invoiced | --not-invoiced]
```

### `projects`

```
clockify projects list             [--name TEXT] [--archived] [--billable]
clockify projects get              <project_id>
clockify projects create           <name> [--color HEX] [--client CLIENT_ID]
clockify projects update           <project_id> [--name TEXT] [--color HEX]
clockify projects delete           <project_id> [--confirm]
clockify projects estimate         <project_id> [--time-type AUTO|MANUAL]
clockify projects members          <project_id> --user-id <id>
clockify projects add-members      <project_id> --user-id <id>
clockify projects template         <project_id> [--is-template | --not-template]
clockify projects user-cost-rate   <project_id> <user_id>
clockify projects user-hourly-rate <project_id> <user_id>
```

### `tasks`

```
clockify tasks list        --project <name_or_id> [--name TEXT]
clockify tasks get         <task_id> --project <name_or_id>
clockify tasks create      <name> --project <name_or_id>
clockify tasks update      <task_id> --project <name_or_id>
clockify tasks delete      <task_id> --project <name_or_id> [--confirm]
clockify tasks cost-rate   <task_id> --project <name_or_id> --amount <n>
clockify tasks hourly-rate <task_id> --project <name_or_id> --amount <n>
```

### `clients`

```
clockify clients list    [--name TEXT] [--archived]
clockify clients get     <client_id>
clockify clients create  <name> [--note TEXT]
clockify clients update  <client_id> [--name TEXT]
clockify clients delete  <client_id> [--confirm]
```

### `tags`

```
clockify tags list    [--name TEXT] [--archived]
clockify tags get     <tag_id>
clockify tags create  <name>
clockify tags update  <tag_id> --name <new_name>
clockify tags delete  <tag_id> [--confirm]
```

### `users`

```
clockify users list            [--name TEXT] [--email TEXT] [--status TEXT]
clockify users me
clockify users filter          [--name TEXT] [--status TEXT] [--role TEXT]
clockify users profile         <user_id>
clockify users update-profile  <user_id> [--name TEXT]
clockify users update-status   <user_id> --status ACTIVE|INACTIVE
clockify users managers        <user_id>
clockify users make-manager    <user_id> --role <ROLE> --entity-id <id>
clockify users remove-manager  <user_id> --role <ROLE> --entity-id <id>
clockify users cost-rate       <user_id> --amount <n>
clockify users hourly-rate     <user_id> --amount <n>
clockify users set-field       <user_id> <field_id> --value <val>
clockify users upload-photo    <file_path>
```

### `workspaces`

```
clockify workspaces list
clockify workspaces get          <workspace_id>
clockify workspaces use          <workspace_id>
clockify workspaces create       <name>
clockify workspaces invite       --email <email>
clockify workspaces cost-rate    --amount <n>
clockify workspaces hourly-rate  --amount <n>
```

### `reports`

```
clockify reports detailed    --start <date> --end <date>
clockify reports summary     --start <date> --end <date>
clockify reports weekly      --start <date> --end <date>
clockify reports attendance  --start <date> --end <date>
clockify reports expense     --start <date> --end <date>
```

### `invoices`

```
clockify invoices list
clockify invoices get              <invoice_id>
clockify invoices create           [--name TEXT]
clockify invoices update           <invoice_id>
clockify invoices delete           <invoice_id> [--confirm]
clockify invoices duplicate        <invoice_id>
clockify invoices export           <invoice_id>
clockify invoices status           <invoice_id> --status <STATUS>
clockify invoices filter
clockify invoices payments list    <invoice_id>
clockify invoices payments add     <invoice_id>
clockify invoices payments delete  <invoice_id> <payment_id>
clockify invoices settings
clockify invoices settings-update
```

### `expenses`

```
clockify expenses list
clockify expenses get               <expense_id>
clockify expenses create
clockify expenses update            <expense_id>
clockify expenses delete            <expense_id> [--confirm]
clockify expenses receipt           <expense_id> <file_id>
clockify expenses categories list
clockify expenses categories create <name>
clockify expenses categories update <id>
clockify expenses categories delete <id> [--confirm]
clockify expenses categories archive <id>
```

### `webhooks`

```
clockify webhooks list
clockify webhooks get           <webhook_id>
clockify webhooks create        --name <n> --url <u> --trigger <event>
clockify webhooks update        <webhook_id>
clockify webhooks delete        <webhook_id> [--confirm]
clockify webhooks logs          <webhook_id>
clockify webhooks regen-token   <webhook_id>
clockify webhooks addon-list    <addon_id>
```

### `approval`

```
clockify approval list
clockify approval submit              --start <d> --end <d>
clockify approval submit-for-user     <user_id> --start <d> --end <d>
clockify approval resubmit            --start <d> --end <d>
clockify approval resubmit-for-user   <user_id> --start <d> --end <d>
clockify approval update              <request_id> --status APPROVED|REJECTED
```

### `time-off`

```
clockify time-off policies list
clockify time-off policies create  --name <n>
clockify time-off policies update  <policy_id> [--name TEXT] [--approve JSON]
                                                [--user UID ...] [--user-group GID ...]
clockify time-off policies delete  <policy_id> [--confirm]
clockify time-off policies status  <policy_id> --status ACTIVE|INACTIVE
clockify time-off balance
clockify time-off request
clockify time-off requests
```

### `scheduling`

```
clockify scheduling assignments list
clockify scheduling assignments create-recurring
clockify scheduling assignments update-recurring  <id>
clockify scheduling assignments delete-recurring  <id> [--confirm]
clockify scheduling assignments update-series     <id>
clockify scheduling assignments copy              <id> --user-id <uid>
clockify scheduling assignments publish
clockify scheduling assignments project-totals    <project_id>
clockify scheduling assignments batch-totals
clockify scheduling assignments user-capacity     <user_id>
clockify scheduling assignments capacity-filter
```

### `shared-reports`

```
clockify shared-reports list
clockify shared-reports get         <report_id>
clockify shared-reports get-public  <report_id>
clockify shared-reports create      <name>
clockify shared-reports update      <report_id>
clockify shared-reports delete      <report_id> [--confirm]
```

### Other

```
clockify groups list|create|update|delete|add-user|remove-user
clockify holidays list|in-period|create|update|delete
clockify custom-fields list|create|update|delete|project
clockify entities created|updated|deleted
clockify config set-profile <name> --api-key <key> [--workspace <id>]
```

## Architecture

The codebase is modular after the God Object refactor:

```
cli_anything/clockify/
├── clockify_cli.py          # Thin root: main group, REPL, add_command calls
├── commands/                # 17 modules (one per CLI domain group) + _helpers.py
│   ├── _helpers.py          # Shared: _ws, _user, _out, handle_errors, set_repl_mode
│   └── <domain>.py          # entries, projects, timer, invoices, expenses, ...
└── core/
    ├── clockify_backend.py  # Thin facade: inherits all 16 mixins
    └── mixins/
        ├── _base.py         # HTTP infrastructure, retry, pagination
        └── _<domain>.py     # 16 domain mixins
```

`ClockifyBackend` composes all mixins via multiple inheritance. Each mixin calls only `_get / _post / _put / _patch / _delete / _get_all_pages / _reports_post` from `_base.py`.

## `commands` Command

List all 161 CLI commands as structured JSON (useful for agents and tooling):

```bash
clockify commands --json
# → [{"name": "start", "group": "timer", "options": [...]}, ...]

clockify commands --json | python3 -c "import json,sys; print(len(json.load(sys.stdin)))"
# → 161
```

Nested groups use slash notation: `"group": "invoices/payments"`, `"group": "time-off/policies"`.

## REPL

Run `clockify` with no subcommand for an interactive shell with tab completion and history.

## Tests

```bash
pip install -e ".[dev]"
.venv/bin/pytest cli_anything/clockify/tests/ -q --tb=short
# → 343 passed in ~0.5s (all mocked, no network)
```

See `cli_anything/clockify/tests/TEST.md` for the full test plan and domain coverage table.
