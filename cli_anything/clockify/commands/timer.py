from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils import repl_skin
from cli_anything.clockify.utils.time_utils import (
    parse_datetime_arg,
)
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, _parse_custom_fields, handle_errors,
)


@click.group()
def timer():
    """Timer management (start, stop, status, restart)."""
    pass


@timer.command("start")
@click.option("--description", "-d", default="", help="Entry description")
@click.option("--project", "-p", default=None, help="Project name or ID")
@click.option("--tag", "-t", "tags", multiple=True, help="Tag name or ID (repeatable)")
@click.option("--task", default=None, help="Task ID")
@click.option("--at", default=None, help="Start time (HH:MM or ISO)")
@click.option("--billable/--no-billable", default=None, help="Billable status")
@click.option("--type", "entry_type", default=None,
              type=click.Choice(["REGULAR", "BREAK"]), help="Entry type")
@click.option("--custom-field", "custom_fields", multiple=True,
              help="Custom field FIELD_ID=VALUE (repeatable)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def timer_start(ctx, description, project, tags, task, at, billable, entry_type, custom_fields, use_json):
    """Start a new running timer."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    uid = _user(ctx)
    project_id = _resolve_project_id(b, ws, project) if project else None
    start = parse_datetime_arg(at) if at else None
    cf = _parse_custom_fields(custom_fields) if custom_fields else None
    entry = b.start_timer(
        ws, uid,
        description=description,
        project_id=project_id,
        tag_ids=list(tags) if tags else None,
        task_id=task,
        start=start,
        billable=billable,
        entry_type=entry_type,
        custom_fields=cf,
    )
    _out(ctx, entry, lambda d: repl_skin.success(
        f"Timer started: {d.get('description', '')} [{d.get('id', '')}]"
    ))


@timer.command("stop")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def timer_stop(ctx, use_json):
    """Stop the running timer."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    uid = _user(ctx)
    entry = b.stop_timer(ws, uid)
    _out(ctx, entry, lambda d: repl_skin.success(
        f"Timer stopped: {d.get('description', '')} [{d.get('id', '')}]"
    ))


@timer.command("status")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def timer_status(ctx, use_json):
    """Show the currently running timer (if any)."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    uid = _user(ctx)
    entry = b.get_running_timer(ws, uid)
    if ctx.obj.get("json"):
        result = {"running": entry is not None}
        if entry:
            result["entry"] = entry
        _out(ctx, result)
    else:
        fmt.print_timer(entry, running=entry is not None)


@timer.command("restart")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def timer_restart(ctx, use_json):
    """Stop running timer (if any) and start a new one with same description."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    uid = _user(ctx)
    running = b.get_running_timer(ws, uid)
    if running:
        b.stop_timer(ws, uid)
    desc = running.get("description", "") if running else ""
    proj_id = running.get("projectId") if running else None
    tag_ids = running.get("tagIds") if running else None
    task_id = running.get("taskId") if running else None
    billable = running.get("billable") if running else None
    entry = b.start_timer(
        ws, uid, description=desc, project_id=proj_id,
        tag_ids=tag_ids, task_id=task_id, billable=billable,
    )
    _out(ctx, entry, lambda d: repl_skin.success(
        f"Timer restarted: {d.get('description', '')} [{d.get('id', '')}]"
    ))
