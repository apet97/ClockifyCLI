from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils import repl_skin
from cli_anything.clockify.utils.time_utils import (
    parse_date_arg,
    parse_datetime_arg,
    date_range_today,
)
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, _parse_custom_fields,
    _parse_custom_attributes, handle_errors,
)


@click.group()
def entries():
    """Time entry management."""
    pass


@entries.command("list")
@click.option("--start", default=None, help="Start date (YYYY-MM-DD or 'today')")
@click.option("--end", default=None, help="End date (YYYY-MM-DD or 'today')")
@click.option("--project", default=None, help="Filter by project name or ID")
@click.option("--task", "task_filter", default=None, help="Filter by task ID")
@click.option("--tag-filter", "tag_filters", multiple=True, help="Filter by tag ID (repeatable)")
@click.option("--description", default=None, help="Filter by description (substring match)")
@click.option("--in-progress", "in_progress", is_flag=True, default=False, help="Show only in-progress entries")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--page", default=None, type=int, help="Page number (single-page fetch)")
@click.option("--page-size", default=50, type=int, help="Items per page (with --page)")
@click.option("--project-required", is_flag=True, default=False, help="Force project field in response")
@click.option("--task-required", is_flag=True, default=False, help="Force task field in response")
@click.option("--hydrated", is_flag=True, default=False, help="Include full project/task/tag objects")
@click.option("--get-week-before", "get_week_before", default=None, help="Get week before date (YYYY-MM-DD)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entries_list(ctx, start, end, project, task_filter, tag_filters, description, in_progress, limit, page, page_size, project_required, task_required, hydrated, get_week_before, use_json):
    """List time entries."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    uid = _user(ctx)
    start_iso = parse_datetime_arg(parse_date_arg(start) + "T00:00:00") if start else None
    end_iso = parse_datetime_arg(parse_date_arg(end) + "T23:59:59") if end else None
    project_id = _resolve_project_id(b, ws, project) if project else None
    if page is not None:
        params: dict = {"page": page, "page-size": page_size}
        if start_iso:
            params["start"] = start_iso
        if end_iso:
            params["end"] = end_iso
        if project_id:
            params["project"] = project_id
        if task_filter:
            params["task"] = task_filter
        if description:
            params["description"] = description
        if in_progress:
            params["in-progress"] = "true"
        if tag_filters:
            params["tags"] = ",".join(tag_filters)
        if project_required:
            params["project-required"] = "true"
        if task_required:
            params["task-required"] = "true"
        if hydrated:
            params["hydrated"] = "true"
        if get_week_before:
            params["get-week-before"] = get_week_before
        path = f"/workspaces/{ws}/user/{uid}/time-entries"
        data = b._get(path, params=params, entity="time entries")
    else:
        data = b.list_entries(
            ws, uid,
            start=start_iso, end=end_iso, project_id=project_id,
            task_id=task_filter or None,
            tags=list(tag_filters) if tag_filters else None,
            description=description or None,
            in_progress=True if in_progress else None,
            hydrated=True if hydrated else None,
            get_week_before=get_week_before or None,
            project_required=True if project_required else None,
            task_required=True if task_required else None,
        )
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_entries)


@entries.command("today")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entries_today(ctx, use_json):
    """List today's time entries."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    uid = _user(ctx)
    start, end = date_range_today()
    data = b.list_entries(ws, uid, start=start, end=end)
    _out(ctx, data, fmt.print_entries)


@entries.command("get")
@click.argument("entry_id")
@click.option("--hydrated", is_flag=True, default=False,
              help="Include full project/task/tag objects")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entries_get(ctx, entry_id, hydrated, use_json):
    """Get a single time entry by ID."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.get_entry(ws, entry_id, hydrated=True if hydrated else None)
    _out(ctx, data)


@entries.command("add")
@click.option("--start", required=True, help="Start (HH:MM, YYYY-MM-DD HH:MM, or ISO)")
@click.option("--end", required=True, help="End (HH:MM, YYYY-MM-DD HH:MM, or ISO)")
@click.option("--description", "-d", default="", help="Entry description")
@click.option("--project", "-p", default=None, help="Project name or ID")
@click.option("--tag", "-t", "tags", multiple=True, help="Tag ID (repeatable)")
@click.option("--task", default=None, help="Task ID (24-character Clockify object ID)")
@click.option("--billable/--no-billable", default=None, help="Mark entry as billable")
@click.option("--type", "entry_type", default=None,
              type=click.Choice(["REGULAR", "BREAK"]),
              help="Entry type (REGULAR, BREAK)")
@click.option("--custom-field", "custom_fields", multiple=True,
              help="Custom field value as FIELD_ID=VALUE (repeatable)")
@click.option("--custom-attribute", "custom_attributes", multiple=True,
              help="Custom attribute as NAMESPACE:NAME=VALUE (repeatable, max 10)")
@click.option("--for-user", default=None, help="Create entry for another user (user ID)")
@click.option("--from-entry", "from_entry", default=None, help="Duplicate an existing time entry by ID")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entries_add(ctx, start, end, description, project, tags, task, billable, entry_type, custom_fields, custom_attributes, for_user, from_entry, use_json):
    """Create a new (completed) time entry."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    uid = for_user or _user(ctx)
    project_id = _resolve_project_id(b, ws, project) if project else None
    body: dict = {
        "start": parse_datetime_arg(start),
        "end": parse_datetime_arg(end),
        "description": description,
    }
    if project_id:
        body["projectId"] = project_id
    if tags:
        body["tagIds"] = list(tags)
    if task:
        body["taskId"] = task
    if billable is not None:
        body["billable"] = billable
    if entry_type:
        body["type"] = entry_type
    if custom_fields:
        body["customFields"] = _parse_custom_fields(custom_fields)
    if custom_attributes:
        body["customAttributes"] = _parse_custom_attributes(custom_attributes)
    entry = b.create_entry(ws, uid, body, from_entry=from_entry)
    _out(ctx, entry, lambda d: repl_skin.success(
        f"Entry created [{d.get('id', '')}]"
    ))


@entries.command("add-direct")
@click.option("--start", required=True, help="Start (HH:MM, YYYY-MM-DD HH:MM, or ISO)")
@click.option("--end", required=True, help="End (HH:MM, YYYY-MM-DD HH:MM, or ISO)")
@click.option("--description", "-d", default="", help="Entry description")
@click.option("--project", "-p", default=None, help="Project name or ID")
@click.option("--tag", "-t", "tags", multiple=True, help="Tag ID (repeatable)")
@click.option("--task", default=None, help="Task ID (24-character Clockify object ID)")
@click.option("--billable/--no-billable", default=None, help="Mark entry as billable")
@click.option("--type", "entry_type", default=None,
              type=click.Choice(["REGULAR", "BREAK"]),
              help="Entry type (REGULAR, BREAK)")
@click.option("--custom-field", "custom_fields", multiple=True,
              help="Custom field value as FIELD_ID=VALUE (repeatable)")
@click.option("--custom-attribute", "custom_attributes", multiple=True,
              help="Custom attribute as NAMESPACE:NAME=VALUE (repeatable, max 10)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entries_add_direct(ctx, start, end, description, project, tags, task, billable, entry_type, custom_fields, custom_attributes, use_json):
    """Create a time entry directly (workspace-scoped, no user ID)."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    project_id = _resolve_project_id(b, ws, project) if project else None
    body: dict = {
        "start": parse_datetime_arg(start),
        "end": parse_datetime_arg(end),
        "description": description,
    }
    if project_id:
        body["projectId"] = project_id
    if tags:
        body["tagIds"] = list(tags)
    if task:
        body["taskId"] = task
    if billable is not None:
        body["billable"] = billable
    if entry_type:
        body["type"] = entry_type
    if custom_fields:
        body["customFields"] = _parse_custom_fields(custom_fields)
    if custom_attributes:
        body["customAttributes"] = _parse_custom_attributes(custom_attributes)
    entry = b.create_time_entry_direct(ws, body)
    _out(ctx, entry, lambda d: repl_skin.success(
        f"Entry created (direct) [{d.get('id', '')}]"
    ))


@entries.command("update")
@click.argument("entry_id")
@click.option("--description", "-d", default=None)
@click.option("--start", default=None)
@click.option("--end", default=None)
@click.option("--project", "-p", default=None)
@click.option("--tag", "-t", "tags", multiple=True, help="Tag ID (repeatable, replaces all tags)")
@click.option("--task", default=None, help="Task ID (24-character Clockify object ID)")
@click.option("--billable/--no-billable", default=None, help="Set billable status")
@click.option("--type", "entry_type", default=None,
              type=click.Choice(["REGULAR", "BREAK"]),
              help="Entry type (REGULAR, BREAK)")
@click.option("--custom-field", "custom_fields", multiple=True,
              help="Custom field value as FIELD_ID=VALUE (repeatable)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entries_update(ctx, entry_id, description, start, end, project, tags, task, billable, entry_type, custom_fields, use_json):
    """Update a time entry."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    existing = b.get_entry(ws, entry_id)
    body = dict(existing)
    if description is not None:
        body["description"] = description
    if start:
        body["start"] = parse_datetime_arg(start)
    if end:
        body["end"] = parse_datetime_arg(end)
    if project:
        body["projectId"] = _resolve_project_id(b, ws, project)
    if tags:
        body["tagIds"] = list(tags)
    if task:
        body["taskId"] = task
    if billable is not None:
        body["billable"] = billable
    if entry_type:
        body["type"] = entry_type
    if custom_fields:
        body["customFields"] = _parse_custom_fields(custom_fields)
    data = b.update_entry(ws, entry_id, body)
    _out(ctx, data, lambda d: repl_skin.success(f"Entry {entry_id} updated."))


@entries.command("delete")
@click.argument("entry_id")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entries_delete(ctx, entry_id, confirm, use_json):
    """Delete a time entry."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"entry {entry_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_entry(ws, entry_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Entry {entry_id} deleted."))


@entries.command("bulk-delete")
@click.option("--ids", required=True, help="Comma-separated entry IDs")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entries_bulk_delete(ctx, ids, confirm, use_json):
    """Bulk delete time entries by ID list."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"entries ({ids})", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    uid = _user(ctx)
    entry_ids = [i.strip() for i in ids.split(",") if i.strip()]
    data = b.bulk_delete_entries(ws, uid, entry_ids)
    _out(ctx, data, lambda _: repl_skin.success(f"Bulk deleted {len(entry_ids)} entries."))


@entries.command("duplicate")
@click.argument("entry_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entries_duplicate(ctx, entry_id, use_json):
    """Duplicate a time entry."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    uid = _user(ctx)
    data = b.duplicate_entry(ws, uid, entry_id)
    _out(ctx, data, lambda d: repl_skin.success(f"Entry duplicated [{d.get('id', '')}]"))


@entries.command("mark-invoiced")
@click.option("--ids", required=True, help="Comma-separated entry IDs")
@click.option("--invoiced/--not-invoiced", default=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entries_mark_invoiced(ctx, ids, invoiced, use_json):
    """Mark time entries as invoiced or not invoiced."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    entry_ids = [i.strip() for i in ids.split(",") if i.strip()]
    data = b.mark_entries_invoiced(ws, entry_ids, invoiced)
    _out(ctx, data, lambda _: repl_skin.success(
        f"Marked {len(entry_ids)} entries as {'invoiced' if invoiced else 'not invoiced'}."
    ))


@entries.command("bulk-update")
@click.option("--ids", required=True, multiple=True, help="Entry ID (repeatable)")
@click.option("--project", default=None, help="Project name or ID")
@click.option("--billable/--no-billable", default=None)
@click.option("--tag", "tags", multiple=True, help="Tag ID (repeatable)")
@click.option("--description", "-d", default=None, help="Entry description")
@click.option("--start", default=None, help="Start time (ISO datetime)")
@click.option("--end", default=None, help="End time (ISO datetime)")
@click.option("--task", default=None, help="Task ID")
@click.option("--type", "entry_type", default=None,
              type=click.Choice(["REGULAR", "BREAK"]),
              help="Entry type")
@click.option("--custom-field", "custom_fields", multiple=True,
              help="Custom field value as FIELD_ID=VALUE (repeatable)")
@click.option("--hydrated", is_flag=True, default=False,
              help="Return enriched response with full project/task/tag objects")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entries_bulk_update(ctx, ids, project, billable, tags, description, start, end, task, entry_type, custom_fields, hydrated, use_json):
    """Bulk update time entries."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    uid = _user(ctx)
    # Build shared update fields
    shared: dict = {}
    if project:
        shared["projectId"] = _resolve_project_id(b, ws, project)
    if billable is not None:
        shared["billable"] = billable
    if tags:
        shared["tagIds"] = list(tags)
    if description is not None:
        shared["description"] = description
    if start:
        shared["start"] = parse_datetime_arg(start)
    if end:
        shared["end"] = parse_datetime_arg(end)
    if task:
        shared["taskId"] = task
    if entry_type:
        shared["type"] = entry_type
    if custom_fields:
        shared["customFields"] = _parse_custom_fields(custom_fields)
    # Spec requires an array of objects, each with an "id" field
    updates = [{"id": entry_id, **shared} for entry_id in ids]
    data = b.bulk_update_entries(ws, uid, updates, hydrated=True if hydrated else None)
    _out(ctx, data, lambda _: repl_skin.success(f"Bulk updated {len(ids)} entries."))
