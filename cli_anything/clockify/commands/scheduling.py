from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils import repl_skin
from cli_anything.clockify.utils.time_utils import (
    parse_date_arg,
)
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, handle_errors,
)


# ── scheduling ────────────────────────────────────────────────────────

@click.group()
def scheduling():
    """Manage scheduling assignments (Enterprise)."""
    pass


@scheduling.group()
def assignments():
    """Scheduling assignment commands."""
    pass


@assignments.command("list")
@click.option("--start", default=None, help="Start date (YYYY-MM-DD)")
@click.option("--end", default=None, help="End date (YYYY-MM-DD)")
@click.option("--user-id", default=None, help="Filter by user ID")
@click.option("--project-id", default=None, help="Filter by project ID")
@click.option("--name", default=None, help="Filter by assignment name")
@click.option("--sort-column", default=None,
              type=click.Choice(["PROJECT", "USER", "ID"]),
              help="Sort column")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
@handle_errors
def assignments_list(ctx, start, end, user_id, project_id, name, sort_column, sort_order, page, page_size, limit, use_json):
    """List all scheduling assignments."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    params = {k: v for k, v in {"start": start, "end": end, "userId": user_id, "projectId": project_id}.items() if v is not None}
    if page is not None:
        params["page"] = page
    if page_size is not None:
        params["page-size"] = page_size
    result = b.list_all_assignments(ws, name=name or None, sort_column=sort_column or None, sort_order=sort_order or None, **params)
    if ctx.obj.get("json"):
        if limit > 0 and isinstance(result, list):
            result = result[:limit]
        fmt.print_json(result)
    else:
        items = result if isinstance(result, list) else result.get("assignments", [result])
        if limit > 0:
            items = items[:limit]
        fmt.print_assignments(items)


@assignments.command("create-recurring")
@click.option("--project-id", required=True, help="Project ID")
@click.option("--user-id", required=True, help="User ID")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD)")
@click.option("--hours", type=float, default=8.0, help="Hours per day")
@click.option("--task-id", "task_id", default=None, help="Task ID")
@click.option("--note", default=None, help="Assignment note (max 100 chars)")
@click.option("--start-time", "start_time", default=None, help="Start time (HH:MM:SS)")
@click.option("--billable/--not-billable", default=None, help="Billable status")
@click.option("--include-non-working-days", "include_non_working_days", is_flag=True, default=False, help="Include non-working days")
@click.option("--weeks", default=None, type=int, help="Recurring period in weeks (1-99)")
@click.option("--repeat/--no-repeat", default=None, help="Enable recurring")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
@handle_errors
def assignments_create_recurring(ctx, project_id, user_id, start, end, hours, task_id, note, start_time, billable, include_non_working_days, weeks, repeat, use_json):
    """Create a recurring assignment."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data: dict = {"projectId": project_id, "userId": user_id, "start": start, "end": end, "hoursPerDay": hours}
    if task_id:
        data["taskId"] = task_id
    if note:
        data["note"] = note
    if start_time:
        data["startTime"] = start_time
    if billable is not None:
        data["billable"] = billable
    if include_non_working_days:
        data["includeNonWorkingDays"] = True
    if weeks is not None or repeat is not None:
        rec: dict = {}
        if weeks is not None:
            rec["weeks"] = weeks
        if repeat is not None:
            rec["repeat"] = repeat
        data["recurringAssignment"] = rec
    result = b.create_recurring_assignment(ws, data)
    _out(ctx, result, lambda d: repl_skin.success(
        f"Created recurring assignment: {d.get('id', result)}"
    ))


@assignments.command("update-recurring")
@click.argument("assignment_id")
@click.option("--start", default=None, help="New start date")
@click.option("--end", default=None, help="New end date")
@click.option("--hours", type=float, default=None, help="Hours per day")
@click.option("--task-id", "task_id", default=None, help="Task ID")
@click.option("--note", default=None, help="Assignment note (max 100 chars)")
@click.option("--start-time", "start_time", default=None, help="Start time (HH:MM:SS)")
@click.option("--billable/--not-billable", default=None, help="Billable status")
@click.option("--include-non-working-days", "include_non_working_days", is_flag=True, default=False, help="Include non-working days")
@click.option("--series-update-option", "series_update_option", default=None,
              type=click.Choice(["THIS_ONE", "THIS_AND_FOLLOWING", "ALL"]),
              help="Which occurrences to update")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
@handle_errors
def assignments_update_recurring(ctx, assignment_id, start, end, hours, task_id, note, start_time, billable, include_non_working_days, series_update_option, use_json):
    """Update a recurring assignment."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data: dict = {}
    if start is not None:
        data["start"] = start
    if end is not None:
        data["end"] = end
    if hours is not None:
        data["hoursPerDay"] = hours
    if task_id is not None:
        data["taskId"] = task_id
    if note is not None:
        data["note"] = note
    if start_time is not None:
        data["startTime"] = start_time
    if billable is not None:
        data["billable"] = billable
    if include_non_working_days:
        data["includeNonWorkingDays"] = True
    if series_update_option:
        data["seriesUpdateOption"] = series_update_option
    result = b.update_recurring_assignment(ws, assignment_id, data)
    _out(ctx, result, lambda _: repl_skin.success(f"Updated assignment {assignment_id}"))


@assignments.command("delete-recurring")
@click.argument("assignment_id")
@click.option("--series-update-option", default=None,
              type=click.Choice(["THIS_ONE", "THIS_AND_FOLLOWING", "ALL"]),
              help="Which occurrences to delete")
@click.option("--confirm", is_flag=True, help="Confirm deletion")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def assignments_delete_recurring(ctx, assignment_id, series_update_option, confirm, use_json):
    """Delete a recurring assignment."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"recurring assignment {assignment_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_recurring_assignment(ws, assignment_id,
                                          series_update_option=series_update_option or None)
    _out(ctx, data, lambda _: repl_skin.success(f"Recurring assignment {assignment_id} deleted."))


@assignments.command("update-series")
@click.argument("assignment_id")
@click.option("--weeks", required=True, type=int, help="Recurring period in weeks (1-99)")
@click.option("--repeat/--no-repeat", default=None, help="Enable recurring")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
@handle_errors
def assignments_update_series(ctx, assignment_id, weeks, repeat, use_json):
    """Change the recurring period of an assignment series."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data: dict = {"weeks": weeks}
    if repeat is not None:
        data["repeat"] = repeat
    result = b.update_recurring_series(ws, assignment_id, data)
    _out(ctx, result, lambda _: repl_skin.success(f"Updated series for assignment {assignment_id}"))


@assignments.command("copy")
@click.argument("assignment_id")
@click.option("--user-id", required=True, help="User ID to copy assignment to")
@click.option("--series-update-option", default=None,
              type=click.Choice(["THIS_ONE", "THIS_AND_FOLLOWING", "ALL"]),
              help="Which occurrences to copy")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
@handle_errors
def assignments_copy(ctx, assignment_id, user_id, series_update_option, use_json):
    """Copy an assignment to another user."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"userId": user_id}
    if series_update_option:
        body["seriesUpdateOption"] = series_update_option
    result = b.copy_assignment(ws, assignment_id, body)
    _out(ctx, result, lambda _: repl_skin.success(f"Copied assignment {assignment_id}"))


@assignments.command("publish")
@click.option("--start", default=None, help="Start date (YYYY-MM-DD, 'today', or 'yesterday')")
@click.option("--end", default=None, help="End date (YYYY-MM-DD, 'today', or 'yesterday')")
@click.option("--notify-users/--no-notify-users", default=None,
              help="Notify users when assignments are published")
@click.option("--search", default=None, help="Search filter")
@click.option("--view-type", default=None,
              type=click.Choice(["PROJECTS", "TEAM", "ALL"]),
              help="View type filter")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
@handle_errors
def assignments_publish(ctx, start, end, notify_users, search, view_type, use_json):
    """Publish pending assignments."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data: dict = {}
    if start:
        data["start"] = parse_date_arg(start)
    if end:
        data["end"] = parse_date_arg(end)
    if notify_users is not None:
        data["notifyUsers"] = notify_users
    if search is not None:
        data["search"] = search
    if view_type is not None:
        data["viewType"] = view_type
    result = b.publish_assignments(ws, data)
    _out(ctx, result, lambda _: repl_skin.success("Assignments published."))


@assignments.command("project-totals")
@click.argument("project_id")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD or ISO datetime)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD or ISO datetime)")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
@handle_errors
def assignments_project_totals(ctx, project_id, start, end, use_json):
    """Get assignment totals for a single project."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    result = b.get_project_assignment_totals(ws, project_id, start=start, end=end)
    if ctx.obj.get("json"):
        fmt.print_json(result)
    else:
        fmt.print_scheduling_totals(result)


@assignments.command("user-capacity")
@click.argument("user_id")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD or ISO datetime)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD or ISO datetime)")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
@handle_errors
def assignments_user_capacity(ctx, user_id, start, end, page, page_size, use_json):
    """Get scheduling capacity for a user."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    result = b.get_user_capacity(ws, user_id, start=start, end=end, page=page, page_size=page_size)
    if ctx.obj.get("json"):
        fmt.print_json(result)
    else:
        fmt.print_scheduling_totals(result)


# ── scheduling extra commands ──────────────────────────────────────────

@assignments.command("batch-totals")
@click.option("--project-id", "project_ids", multiple=True, required=True,
              help="Project ID (repeatable)")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--search", default=None, help="Filter projects by name")
@click.option("--status-filter", default=None,
              type=click.Choice(["PUBLISHED", "UNPUBLISHED", "ALL"]),
              help="Filter by publish status")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def assignments_batch_totals(ctx, project_ids, page, page_size, search, status_filter, use_json):
    """Get assignment totals for multiple projects in one call."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"projectIds": list(project_ids)}
    if page is not None:
        body["page"] = page
    if page_size is not None:
        body["pageSize"] = page_size
    if search is not None:
        body["search"] = search
    if status_filter is not None:
        body["statusFilter"] = status_filter
    result = b.get_project_assignments_batch(ws, body)
    if ctx.obj.get("json"):
        fmt.print_json(result)
    else:
        fmt.print_scheduling_totals(result)


@assignments.command("capacity-filter")
@click.option("--user-id", "user_ids", multiple=True, required=True,
              help="User ID (repeatable)")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--search", default=None, help="Filter by user name/email")
@click.option("--status-filter", default=None,
              type=click.Choice(["PUBLISHED", "UNPUBLISHED", "ALL"]),
              help="Filter by publish status")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def assignments_capacity_filter(ctx, user_ids, page, page_size, search, status_filter, use_json):
    """Get capacity totals for multiple users in one call."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"userIds": list(user_ids)}
    if page is not None:
        body["page"] = page
    if page_size is not None:
        body["pageSize"] = page_size
    if search is not None:
        body["search"] = search
    if status_filter is not None:
        body["statusFilter"] = status_filter
    result = b.get_users_capacity_filter(ws, body)
    if ctx.obj.get("json"):
        fmt.print_json(result)
    else:
        fmt.print_scheduling_totals(result)
