"""Shared helpers for all Clockify CLI command modules.

Imported by every command module — never imports from clockify_cli.py.
"""

from __future__ import annotations

import functools
import json
import sys

import click

from cli_anything.clockify.core.clockify_backend import ClockifyAPIError
from cli_anything.clockify.utils import formatters as fmt


def _parse_json_option(value: str, option_name: str):
    """Parse a JSON string from a CLI option, raising click.BadParameter on failure."""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError) as e:
        raise click.BadParameter(f"Invalid JSON for {option_name}: {e}")


# ── REPL mode state ────────────────────────────────────────────────────
# Mutated by clockify_cli._run_repl via set_repl_mode(); checked in
# handle_errors() to suppress sys.exit(1) during interactive REPL.

_repl_mode: bool = False


def set_repl_mode(value: bool) -> None:
    """Called by the REPL loop to suppress sys.exit in error handler."""
    global _repl_mode
    _repl_mode = value


# ── Context helpers ────────────────────────────────────────────────────

def _make_session(ctx: click.Context):
    return ctx.obj["session"]


def _make_backend(ctx: click.Context):
    if ctx.obj.get("init_error"):
        raise click.UsageError(ctx.obj["init_error"])
    return ctx.obj["backend"]


def _ws(ctx: click.Context) -> str:
    """Resolve and cache workspace_id on the context object."""
    session = _make_session(ctx)
    backend = _make_backend(ctx)
    return session.resolve_workspace(backend)


def _user(ctx: click.Context) -> str:
    """Resolve and cache user_id."""
    session = _make_session(ctx)
    backend = _make_backend(ctx)
    return session.resolve_user(backend)


def _out(ctx: click.Context, data, human_fn=None):
    """Output data in JSON or human-readable format."""
    if ctx.obj.get("json"):
        fmt.print_json(data)
    elif human_fn:
        human_fn(data)
    else:
        if isinstance(data, (dict, list)):
            fmt.print_json(data)
        else:
            click.echo(str(data))


def _resolve_project_id(backend, workspace_id: str, value: str) -> str:
    """Accept project name or ID; return ID."""
    if len(value) == 24 and all(c in "0123456789abcdefABCDEF" for c in value):
        return value
    projects = backend.list_projects(workspace_id, name=value)
    if not projects:
        raise click.UsageError(f"No project found with name '{value}'")
    return projects[0]["id"]


def _parse_custom_fields(raw_fields: tuple) -> list[dict]:
    """Parse --custom-field FIELD_ID=VALUE pairs."""
    result = []
    for pair in raw_fields:
        if "=" not in pair:
            raise click.UsageError(f"Custom field must be FIELD_ID=VALUE, got: {pair}")
        fid, val = pair.split("=", 1)
        if not fid.strip():
            raise click.UsageError(f"Custom field ID cannot be empty in: {pair}")
        result.append({"customFieldId": fid, "value": val})
    return result


def _parse_custom_attributes(raw_attrs: tuple) -> list[dict]:
    """Parse --custom-attribute NAMESPACE:NAME=VALUE triples."""
    result = []
    for attr in raw_attrs:
        if "=" not in attr:
            raise click.UsageError(
                f"Custom attribute must be NAMESPACE:NAME=VALUE, got: {attr}"
            )
        key, value = attr.split("=", 1)
        if ":" not in key:
            raise click.UsageError(
                f"Expected NAMESPACE:NAME before '=', got: {key}"
            )
        namespace, name = key.split(":", 1)
        if not namespace.strip():
            raise click.UsageError(f"Namespace cannot be empty in: {attr}")
        if not name.strip():
            raise click.UsageError(f"Name cannot be empty in: {attr}")
        result.append({"namespace": namespace, "name": name, "value": value})
    return result


def _confirm_destructive(ctx: click.Context, name: str, confirm: bool) -> None:
    """Prompt for confirmation unless --confirm or --json mode."""
    if confirm or ctx.obj.get("json"):
        return
    click.confirm(f"Delete {name}?", abort=True)


# ── Error decorator ────────────────────────────────────────────────────

def handle_errors(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ClockifyAPIError as e:
            ctx_arg = next(
                (a for a in args if isinstance(a, click.Context)), None
            )
            if ctx_arg and ctx_arg.obj and ctx_arg.obj.get("json"):
                fmt.print_json({"error": str(e), "status_code": e.status_code})
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except click.exceptions.Abort:
            click.echo("Aborted.")
        except Exception as e:
            ctx_arg = next(
                (a for a in args if isinstance(a, click.Context)), None
            )
            if ctx_arg and ctx_arg.obj and ctx_arg.obj.get("json"):
                fmt.print_json({"error": str(e), "type": type(e).__name__})
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    return wrapper
