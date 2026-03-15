from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils import repl_skin
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, handle_errors,
)


@click.group()
def tasks():
    """Task management (require --project)."""
    pass


@tasks.command("list")
@click.option("--project", "-p", required=True, help="Project name or ID")
@click.option("--name", default=None, help="Filter by task name")
@click.option("--is-active", "is_active", is_flag=True, default=False, help="Filter active tasks only")
@click.option("--strict-name-search", is_flag=True, default=False, help="Exact name match")
@click.option("--sort-column", default=None,
              type=click.Choice(["ID", "NAME"]),
              help="Sort column")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--page", default=None, type=int, help="Page number (1-based)")
@click.option("--page-size", "page_size", default=None, type=int, help="Items per page")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def tasks_list(ctx, project, name, is_active, strict_name_search, sort_column, sort_order, page, page_size, limit, use_json):
    """List tasks for a project."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    proj_id = _resolve_project_id(b, ws, project)
    data = b.list_tasks(ws, proj_id, name=name or None, is_active=True if is_active else None, strict_name_search=True if strict_name_search else None, sort_column=sort_column or None, sort_order=sort_order or None, page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_tasks)


@tasks.command("create")
@click.argument("name")
@click.option("--project", "-p", required=True, help="Project name or ID")
@click.option("--assignee-id", "assignee_ids", multiple=True, help="Assignee user ID (repeatable, 24-character Clockify object ID)")
@click.option("--user-group-id", "user_group_ids", multiple=True, help="User group ID (repeatable)")
@click.option("--estimate", default=None, help="Time estimate in ISO 8601 duration, e.g. PT8H or PT1H30M")
@click.option("--budget-estimate", default=None, type=int, help="Budget estimate in cents (min: 0)")
@click.option("--status", default="ACTIVE", type=click.Choice(["ACTIVE", "DONE", "ALL"]),
              help="Initial task status (default: ACTIVE)")
@click.option("--billable/--no-billable", default=None, help="Set billable status")
@click.option("--contains-assignee/--no-contains-assignee", "contains_assignee",
              default=None, help="Include assignee info in response (default: true)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def tasks_create(ctx, name, project, assignee_ids, user_group_ids, estimate, budget_estimate, status, billable, contains_assignee, use_json):
    """Create a task."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    proj_id = _resolve_project_id(b, ws, project)
    body: dict = {"name": name, "status": status}
    if assignee_ids:
        body["assigneeIds"] = list(assignee_ids)
    if user_group_ids:
        body["userGroupIds"] = list(user_group_ids)
    if estimate:
        body["estimate"] = estimate
    if budget_estimate is not None:
        body["budgetEstimate"] = budget_estimate
    if billable is not None:
        body["billable"] = billable
    data = b.create_task(ws, proj_id, body, contains_assignee=contains_assignee)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Task created: {d.get('name', '')} [{d.get('id', '')}]"
    ))


@tasks.command("update")
@click.argument("task_id")
@click.option("--project", "-p", required=True)
@click.option("--name", default=None)
@click.option("--status", type=click.Choice(["ACTIVE", "DONE", "ALL"]), default=None)
@click.option("--assignee-id", "assignee_ids", multiple=True, help="Assignee user ID (repeatable, replaces all assignees)")
@click.option("--user-group-id", "user_group_ids", multiple=True, help="User group ID (repeatable)")
@click.option("--estimate", default=None, help="Time estimate in ISO 8601 duration, e.g. PT8H or PT1H30M")
@click.option("--budget-estimate", default=None, type=int, help="Budget estimate in cents (min: 0)")
@click.option("--billable/--no-billable", default=None, help="Set billable status")
@click.option("--contains-assignee/--no-contains-assignee", default=None,
              help="Filter response to include assignee info")
@click.option("--membership-status", default=None,
              type=click.Choice(["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"]),
              help="Filter membership status in response")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def tasks_update(ctx, task_id, project, name, status, assignee_ids, user_group_ids, estimate, budget_estimate, billable, contains_assignee, membership_status, use_json):
    """Update a task."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    proj_id = _resolve_project_id(b, ws, project)
    existing = b.get_task(ws, proj_id, task_id)
    body = dict(existing)
    if name:
        body["name"] = name
    if status:
        body["status"] = status
    if assignee_ids:
        body["assigneeIds"] = list(assignee_ids)
    if user_group_ids:
        body["userGroupIds"] = list(user_group_ids)
    if estimate:
        body["estimate"] = estimate
    if budget_estimate is not None:
        body["budgetEstimate"] = budget_estimate
    if billable is not None:
        body["billable"] = billable
    data = b.update_task(ws, proj_id, task_id, body,
                         contains_assignee=contains_assignee,
                         membership_status=membership_status or None)
    _out(ctx, data, lambda _: repl_skin.success(f"Task {task_id} updated."))


@tasks.command("get")
@click.argument("task_id")
@click.option("--project", "project_id", required=True, help="Project ID")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def tasks_get(ctx, task_id, project_id, use_json):
    """Get a single task by ID."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    result = b.get_task(ws, project_id, task_id)
    _out(ctx, result, lambda d: click.echo(f"Task: {d.get('name', d.get('id', task_id))}"))


@tasks.command("delete")
@click.argument("task_id")
@click.option("--project", "-p", required=True)
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def tasks_delete(ctx, task_id, project, confirm, use_json):
    """Delete a task."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"task {task_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    proj_id = _resolve_project_id(b, ws, project)
    data = b.delete_task(ws, proj_id, task_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Task {task_id} deleted."))


@tasks.command("cost-rate")
@click.argument("task_id")
@click.option("--project", "-p", required=True)
@click.option("--amount", required=True, type=int, help="Cost rate amount in cents (integer)")
@click.option("--since", default=None, help="Effective date (ISO datetime)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def tasks_cost_rate(ctx, task_id, project, amount, since, use_json):
    """Set a task's cost rate."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    proj_id = _resolve_project_id(b, ws, project)
    body: dict = {"amount": amount}
    if since is not None:
        body["since"] = since
    data = b.update_task_cost_rate(ws, proj_id, task_id, body)
    _out(ctx, data, lambda _: repl_skin.success(f"Task {task_id} cost rate updated."))


@tasks.command("hourly-rate")
@click.argument("task_id")
@click.option("--project", "-p", required=True)
@click.option("--amount", required=True, type=int, help="Hourly rate amount in cents (integer)")
@click.option("--since", default=None, help="Effective date (ISO datetime)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def tasks_hourly_rate(ctx, task_id, project, amount, since, use_json):
    """Set a task's hourly rate."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    proj_id = _resolve_project_id(b, ws, project)
    body: dict = {"amount": amount}
    if since is not None:
        body["since"] = since
    data = b.update_task_hourly_rate(ws, proj_id, task_id, body)
    _out(ctx, data, lambda _: repl_skin.success(f"Task {task_id} hourly rate updated."))
