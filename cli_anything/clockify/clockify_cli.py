#!/usr/bin/env python3
"""Clockify CLI — Full time tracking from the command line.

Usage:
    # List workspaces
    clockify workspaces list

    # Start a timer
    clockify timer start --description "Coding" --project "My Project"

    # Stop timer
    clockify timer stop

    # List today's entries
    clockify entries today --json

    # Summary report
    clockify reports summary --start 2026-03-01 --end 2026-03-13 --json

    # Interactive REPL
    clockify
"""

from __future__ import annotations

import json
import shlex

import click

from cli_anything.clockify.core.clockify_backend import ClockifyBackend
from cli_anything.clockify.utils.session import Session
from cli_anything.clockify.utils import repl_skin

from cli_anything.clockify.commands._helpers import set_repl_mode, _parse_json_option


# ── Root group ────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--api-key", envvar="CLOCKIFY_API_KEY", default=None,
              help="Clockify API key (or set CLOCKIFY_API_KEY)")
@click.option("--workspace", envvar="CLOCKIFY_WORKSPACE_ID", default=None,
              help="Workspace ID (or set CLOCKIFY_WORKSPACE_ID)")
@click.option("--base-url", envvar="CLOCKIFY_BASE_URL", default=None,
              help="API base URL override")
@click.option("--reports-url", envvar="CLOCKIFY_REPORTS_URL", default=None,
              help="Reports API URL override")
@click.option("--json", "use_json", is_flag=True,
              help="Output as JSON (agent-friendly)")
@click.option("--extra-body", "extra_body_json", default=None,
              help="Extra JSON to deep-merge into request body (for advanced API fields)")
@click.option("--verbose", "-v", is_flag=True, default=False,
              help="Log HTTP method/URL/status to stderr")
@click.option("--debug", "debug_mode", is_flag=True, default=False,
              help="Log HTTP details including request body to stderr")
@click.option("--dry-run", "dry_run", is_flag=True, default=False,
              help="Print request details as JSON without sending (sensitive fields redacted)")
@click.option("--timeout", "timeout_seconds", default=None, type=int,
              help="HTTP timeout in seconds (default: 30, reports/uploads: 60)")
@click.option("--profile", envvar="CLOCKIFY_PROFILE", default="default",
              help="Config profile name (default: 'default')")
@click.pass_context
def main(ctx, api_key, workspace, base_url, reports_url, use_json, extra_body_json, verbose, debug_mode, dry_run, timeout_seconds, profile):
    """Clockify CLI — Time tracking from the command line.

    Run without a subcommand to enter interactive REPL mode.
    """
    ctx.ensure_object(dict)
    ctx.obj["json"] = use_json

    # Build session + backend (lazy — only needed if a command runs)
    try:
        session = Session.resolve(
            api_key=api_key,
            workspace_id=workspace,
            base_url=base_url,
            reports_url=reports_url,
            profile=profile,
        )
        if workspace:
            session.workspace_id = workspace
        ctx.obj["session"] = session
        backend = ClockifyBackend(session)
        if extra_body_json:
            backend.extra_body = _parse_json_option(extra_body_json, "--extra-body")
        backend.verbose = verbose or debug_mode
        backend.debug = debug_mode
        backend.dry_run = dry_run
        if timeout_seconds is not None:
            backend.timeout = timeout_seconds
            backend.reports_timeout = max(timeout_seconds, 60)
        ctx.obj["backend"] = backend
    except ValueError as e:
        ctx.obj["session"] = None
        ctx.obj["backend"] = None
        ctx.obj["init_error"] = str(e)

    if ctx.invoked_subcommand is None:
        _run_repl(ctx)


# ── REPL ──────────────────────────────────────────────────────────────

def _run_repl(ctx: click.Context) -> None:
    set_repl_mode(True)

    ws_name = ""
    if ctx.obj.get("session") and ctx.obj["session"].workspace_id:
        ws_name = ctx.obj["session"].workspace_id

    repl_skin.print_banner(ws_name)
    pt = repl_skin.create_prompt_session(repl_skin.REPL_COMPLETIONS)

    help_commands = {
        "timer":      "start|stop|status|restart",
        "entries":    "list|get|add|update|delete|today",
        "projects":   "list|get|create|update|delete",
        "clients":    "list|create|update|delete",
        "tags":       "list|create|update|delete",
        "tasks":      "list|create|update|delete  (require --project)",
        "workspaces": "list|use",
        "users":      "list|me",
        "reports":    "detailed|summary|weekly",
        "help":       "Show this help",
        "quit":       "Exit REPL",
    }

    while True:
        try:
            line = repl_skin.get_input(pt, context=ws_name)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                repl_skin.print_goodbye()
                break
            if line.lower() == "help":
                for cmd, desc in help_commands.items():
                    click.echo(f"  {cmd:<12} {desc}")
                continue

            try:
                args = shlex.split(line)
                main.main(
                    args,
                    standalone_mode=False,
                    obj=ctx.obj,
                )
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                repl_skin.warning(f"Usage error: {e}")
            except click.exceptions.Abort:
                pass
            except Exception as e:
                repl_skin.error(str(e))

        except (EOFError, KeyboardInterrupt):
            repl_skin.print_goodbye()
            break

    set_repl_mode(False)
    if ctx.obj.get("backend"):
        ctx.obj["backend"].close()


# ── Command groups ─────────────────────────────────────────────────────

from cli_anything.clockify.commands.timer import timer
from cli_anything.clockify.commands.entries import entries
from cli_anything.clockify.commands.projects import projects
from cli_anything.clockify.commands.clients import clients
from cli_anything.clockify.commands.tags import tags
from cli_anything.clockify.commands.tasks import tasks
from cli_anything.clockify.commands.workspaces import workspaces
from cli_anything.clockify.commands.users import users
from cli_anything.clockify.commands.reports import reports
from cli_anything.clockify.commands.webhooks import webhooks
from cli_anything.clockify.commands.invoices import invoices
from cli_anything.clockify.commands.expenses import expenses
from cli_anything.clockify.commands.approval import approval
from cli_anything.clockify.commands.time_off import time_off
from cli_anything.clockify.commands.scheduling import scheduling
from cli_anything.clockify.commands.shared_reports import shared_reports
from cli_anything.clockify.commands.misc import (
    groups,
    holidays,
    custom_fields,
    entities,
    config,
)

main.add_command(timer)
main.add_command(entries)
main.add_command(projects)
main.add_command(clients)
main.add_command(tags)
main.add_command(tasks)
main.add_command(workspaces)
main.add_command(users)
main.add_command(reports)
main.add_command(webhooks)
main.add_command(invoices)
main.add_command(expenses)
main.add_command(approval)
main.add_command(time_off)
main.add_command(scheduling)
main.add_command(shared_reports)
main.add_command(groups)
main.add_command(holidays)
main.add_command(custom_fields)
main.add_command(entities)
main.add_command(config)


# ── Commands manifest ─────────────────────────────────────────────────

def _walk_group(group_cmd, group_path: str, manifest: list):
    """Recursively walk a command group, collecting leaf commands."""
    for name, cmd in group_cmd.commands.items():
        if hasattr(cmd, "commands"):
            _walk_group(cmd, f"{group_path}/{name}", manifest)
        else:
            options = [p.name for p in cmd.params if isinstance(p, click.Option)]
            manifest.append({"name": name, "group": group_path, "options": options})


@main.command("commands")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def commands_manifest(ctx, use_json):
    """List all available commands as a structured manifest."""
    manifest = []
    for group_name, group_cmd in main.commands.items():
        if hasattr(group_cmd, "commands"):
            _walk_group(group_cmd, group_name, manifest)
        else:
            options = [p.name for p in group_cmd.params if isinstance(p, click.Option)]
            manifest.append({"name": group_name, "group": "", "options": options})
    click.echo(json.dumps(manifest))
