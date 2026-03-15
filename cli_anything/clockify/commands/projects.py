from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils import repl_skin
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, handle_errors,
)

# ── projects ──────────────────────────────────────────────────────────

@click.group()
def projects():
    """Project management."""
    pass


@projects.command("list")
@click.option("--name", default=None, help="Filter by name")
@click.option("--archived", is_flag=True, default=False, help="Include archived")
@click.option("--billable", "billable_flag", is_flag=True, default=False, help="Filter billable projects only")
@click.option("--client-id", "client_ids", multiple=True, help="Filter by client ID (repeatable)")
@click.option("--strict-name-search", is_flag=True, default=False, help="Exact name match")
@click.option("--contains-client", is_flag=True, default=False, help="Filter projects that have a client")
@click.option("--client-status", default=None,
              type=click.Choice(["ACTIVE", "ARCHIVED", "ALL"]),
              help="Filter by client status")
@click.option("--contains-user", is_flag=True, default=False, help="Filter projects containing current user")
@click.option("--user-status", default=None,
              type=click.Choice(["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"]),
              help="Filter by user membership status")
@click.option("--contains-group", is_flag=True, default=False, help="Filter projects containing a user group")
@click.option("--user-group", "user_groups", multiple=True, help="Filter by user group ID (repeatable)")
@click.option("--is-template", is_flag=True, default=False, help="Filter template projects only")
@click.option("--hydrated", is_flag=True, default=False, help="Include full member/task objects")
@click.option("--access", default=None,
              type=click.Choice(["PUBLIC", "PRIVATE"]),
              help="Filter by project visibility")
@click.option("--sort-column", default=None,
              type=click.Choice(["ID", "NAME", "CLIENT_NAME", "DURATION", "BUDGET", "PROGRESS"]),
              help="Sort column")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--user", "users", multiple=True, help="Filter by user ID (repeatable)")
@click.option("--expense-limit", "expense_limit", default=None, type=int, help="Max expenses to include (default: 20)")
@click.option("--expense-date", "expense_date", default=None, help="Expense date filter (YYYY-MM-DD)")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def projects_list(ctx, name, archived, billable_flag, client_ids, strict_name_search, contains_client, client_status, contains_user, user_status, contains_group, user_groups, is_template, hydrated, access, sort_column, sort_order, users, expense_limit, expense_date, page, page_size, limit, use_json):
    """List projects."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_projects(
        ws,
        name=name,
        archived=archived if archived else None,
        billable=True if billable_flag else None,
        client_ids=list(client_ids) if client_ids else None,
        strict_name_search=True if strict_name_search else None,
        contains_client=True if contains_client else None,
        client_status=client_status or None,
        contains_user=True if contains_user else None,
        user_status=user_status or None,
        contains_group=True if contains_group else None,
        user_groups=list(user_groups) if user_groups else None,
        is_template=True if is_template else None,
        hydrated=True if hydrated else None,
        access=access or None,
        sort_column=sort_column or None,
        sort_order=sort_order or None,
        users=list(users) if users else None,
        expense_limit=expense_limit,
        expense_date=expense_date,
        page=page,
        page_size=page_size if page_size else 50,
    )
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_projects)


@projects.command("get")
@click.argument("project_id")
@click.option("--hydrated", is_flag=True, default=False, help="Include full member/task objects")
@click.option("--custom-field-entity-type", default=None, help="Custom field entity type (default: TIMEENTRY)")
@click.option("--expense-limit", default=None, type=int, help="Max expenses to include (default: 20)")
@click.option("--expense-date", default=None, help="Expense date filter (YYYY-MM-DD)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def projects_get(ctx, project_id, hydrated, custom_field_entity_type, expense_limit, expense_date, use_json):
    """Get a project by ID."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.get_project(
        ws, project_id,
        hydrated=True if hydrated else None,
        custom_field_entity_type=custom_field_entity_type or None,
        expense_limit=expense_limit,
        expense_date=expense_date or None,
    )
    _out(ctx, data)


@projects.command("create")
@click.argument("name")
@click.option("--color", default="#0000FF", help="Project color (hex, e.g. #FF0000)")
@click.option("--client", default=None, help="Client ID (24-character Clockify object ID)")
@click.option("--public", is_flag=True, help="Make project public")
@click.option("--billable/--no-billable", default=None, help="Set billable status")
@click.option("--note", default=None, help="Project note (max 16384 chars)")
@click.option("--hourly-rate", "hourly_rate", default=None, type=float, help="Hourly rate amount (decimal, e.g. 50.0)")
@click.option("--cost-rate", "cost_rate", default=None, type=float, help="Cost rate amount (decimal, e.g. 50.0)")
@click.option("--currency", default="USD", help="3-letter ISO currency code, e.g. USD, EUR, GBP")
@click.option("--estimate-type", default=None, type=click.Choice(["AUTO", "MANUAL"]),
              help="Estimate type")
@click.option("--estimate", default=None, help="Estimate value (e.g. PT8H for time, or integer for budget)")
@click.option("--budget-estimate", "budget_estimate", default=None, type=int, help="Budget estimate amount (integer)")
@click.option("--budget-estimate-reset", "budget_estimate_reset", default=None,
              type=click.Choice(["WEEKLY", "MONTHLY", "YEARLY"]),
              help="Budget estimate reset period")
@click.option("--time-estimate", "time_estimate", default=None, help="Time estimate in ms (e.g. 3600000 for 1h)")
@click.option("--time-estimate-reset", "time_estimate_reset", default=None,
              type=click.Choice(["WEEKLY", "MONTHLY", "YEARLY"]),
              help="Time estimate reset period")
@click.option("--template", "is_template", is_flag=True, default=False, help="Create as a template project")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def projects_create(ctx, name, color, client, public, billable, note, hourly_rate, cost_rate, currency, estimate_type, estimate, budget_estimate, budget_estimate_reset, time_estimate, time_estimate_reset, is_template, use_json):
    """Create a new project."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"name": name, "color": color, "isPublic": public}
    if client:
        body["clientId"] = client
    if billable is not None:
        body["billable"] = billable
    if note:
        body["note"] = note
    if hourly_rate is not None:
        body["hourlyRate"] = {"amount": hourly_rate, "currency": currency}
    if cost_rate is not None:
        body["costRate"] = {"amount": cost_rate, "currency": currency}
    if estimate is not None or estimate_type is not None:
        body["estimate"] = {
            "estimate": estimate or "",
            "type": estimate_type or "AUTO",
        }
    if budget_estimate is not None:
        be: dict = {"estimate": budget_estimate, "active": True}
        if budget_estimate_reset:
            be["resetOption"] = budget_estimate_reset
        body["budgetEstimate"] = be
    if time_estimate is not None:
        te: dict = {"estimate": time_estimate, "active": True}
        if time_estimate_reset:
            te["resetOption"] = time_estimate_reset
        body["timeEstimate"] = te
    if is_template:
        body["isTemplate"] = True
    data = b.create_project(ws, body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Project created: {d.get('name', '')} [{d.get('id', '')}]"
    ))


@projects.command("update")
@click.argument("project_id")
@click.option("--name", default=None)
@click.option("--color", default=None, help="Hex color code, e.g. #FF0000")
@click.option("--archived", is_flag=True, default=False)
@click.option("--billable/--no-billable", default=None, help="Set billable status")
@click.option("--public/--private", "is_public", default=None, help="Set project visibility")
@click.option("--client", "client_id", default=None, help="Client ID (24-character Clockify object ID)")
@click.option("--note", default=None, help="Project note (max 16384 chars)")
@click.option("--hourly-rate", "hourly_rate", default=None, type=float, help="Hourly rate amount (decimal)")
@click.option("--cost-rate", "cost_rate", default=None, type=float, help="Cost rate amount (decimal)")
@click.option("--budget-estimate", "budget_estimate", default=None, type=int, help="Budget estimate amount (integer)")
@click.option("--budget-estimate-reset", "budget_estimate_reset", default=None,
              type=click.Choice(["WEEKLY", "MONTHLY", "YEARLY"]),
              help="Budget estimate reset period")
@click.option("--time-estimate", "time_estimate", default=None, help="Time estimate in ms")
@click.option("--time-estimate-reset", "time_estimate_reset", default=None,
              type=click.Choice(["WEEKLY", "MONTHLY", "YEARLY"]),
              help="Time estimate reset period")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def projects_update(ctx, project_id, name, color, archived, billable, is_public, client_id, note, hourly_rate, cost_rate, budget_estimate, budget_estimate_reset, time_estimate, time_estimate_reset, use_json):
    """Update a project."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    existing = b.get_project(ws, project_id)
    body = dict(existing)
    if name:
        body["name"] = name
    if color:
        body["color"] = color
    if archived:
        body["archived"] = True
    if billable is not None:
        body["billable"] = billable
    if is_public is not None:
        body["isPublic"] = is_public
    if client_id:
        body["clientId"] = client_id
    if note is not None:
        body["note"] = note
    if hourly_rate is not None:
        existing_hr = existing.get("hourlyRate") or {}
        body["hourlyRate"] = {"amount": hourly_rate, "currency": existing_hr.get("currency", "USD")}
    if cost_rate is not None:
        existing_cr = existing.get("costRate") or {}
        body["costRate"] = {"amount": cost_rate, "currency": existing_cr.get("currency", "USD")}
    if budget_estimate is not None:
        be: dict = {"estimate": budget_estimate, "active": True}
        if budget_estimate_reset:
            be["resetOption"] = budget_estimate_reset
        body["budgetEstimate"] = be
    if time_estimate is not None:
        te: dict = {"estimate": time_estimate, "active": True}
        if time_estimate_reset:
            te["resetOption"] = time_estimate_reset
        body["timeEstimate"] = te
    data = b.update_project(ws, project_id, body)
    _out(ctx, data, lambda _: repl_skin.success(f"Project {project_id} updated."))


@projects.command("delete")
@click.argument("project_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def projects_delete(ctx, project_id, confirm, use_json):
    """Delete a project."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"project {project_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_project(ws, project_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Project {project_id} deleted."))


# ── projects (additional commands) ────────────────────────────────────

@projects.command("estimate")
@click.argument("project_id")
@click.option("--time-type", "time_type", default=None,
              type=click.Choice(["AUTO", "MANUAL"]),
              help="Time estimate type")
@click.option("--time-estimate", "time_estimate", default=None,
              help="Duration estimate (ISO-8601, e.g. PT8H)")
@click.option("--time-active/--time-inactive", "time_active", default=None,
              help="Activate/deactivate time estimate")
@click.option("--time-reset", "time_reset", default=None,
              type=click.Choice(["WEEKLY", "MONTHLY", "YEARLY"]),
              help="Time estimate reset interval")
@click.option("--time-include-non-billable/--no-time-include-non-billable",
              "time_include_non_billable", default=None,
              help="Include non-billable in time estimate")
@click.option("--budget-type", "budget_type", default=None,
              type=click.Choice(["AUTO", "MANUAL"]),
              help="Budget estimate type")
@click.option("--budget-estimate", "budget_estimate", default=None, type=int,
              help="Budget estimate amount (min: 0)")
@click.option("--budget-active/--budget-inactive", "budget_active", default=None,
              help="Activate/deactivate budget estimate")
@click.option("--budget-reset", "budget_reset", default=None,
              type=click.Choice(["WEEKLY", "MONTHLY", "YEARLY"]),
              help="Budget estimate reset interval")
@click.option("--budget-include-expenses/--no-budget-include-expenses",
              "budget_include_expenses", default=None,
              help="Include expenses in budget estimate")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def projects_estimate(ctx, project_id, time_type, time_estimate, time_active, time_reset, time_include_non_billable, budget_type, budget_estimate, budget_active, budget_reset, budget_include_expenses, use_json):
    """Update a project's time and budget estimates."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {}
    time_obj: dict = {}
    if time_type:
        time_obj["type"] = time_type
    if time_estimate:
        time_obj["estimate"] = time_estimate
    if time_active is not None:
        time_obj["active"] = time_active
    if time_reset:
        time_obj["resetOption"] = time_reset
    if time_include_non_billable is not None:
        time_obj["includeNonBillable"] = time_include_non_billable
    if time_obj:
        body["timeEstimate"] = time_obj
    budget_obj: dict = {}
    if budget_type:
        budget_obj["type"] = budget_type
    if budget_estimate is not None:
        budget_obj["estimate"] = budget_estimate
    if budget_active is not None:
        budget_obj["active"] = budget_active
    if budget_reset:
        budget_obj["resetOption"] = budget_reset
    if budget_include_expenses is not None:
        budget_obj["includeExpenses"] = budget_include_expenses
    if budget_obj:
        body["budgetEstimate"] = budget_obj
    data = b.update_project_estimate(ws, project_id, body)
    _out(ctx, data, lambda _: repl_skin.success(f"Project {project_id} estimate updated."))


@projects.command("members")
@click.argument("project_id")
@click.option("--user-id", required=True, help="User ID to add/update")
@click.option("--hourly-rate", default=None, type=int, help="Hourly rate amount (integer, e.g. 5000)")
@click.option("--cost-rate", default=None, type=int, help="Cost rate amount (integer, e.g. 3000)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def projects_members(ctx, project_id, user_id, hourly_rate, cost_rate, use_json):
    """Update project memberships."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    membership: dict = {"userId": user_id}
    if hourly_rate is not None:
        membership["hourlyRate"] = {"amount": hourly_rate}
    if cost_rate is not None:
        membership["costRate"] = {"amount": cost_rate}
    body = {"memberships": [membership]}
    data = b.update_project_memberships(ws, project_id, body)
    _out(ctx, data, lambda _: repl_skin.success(f"Project {project_id} memberships updated."))


@projects.command("template")
@click.argument("project_id")
@click.option("--is-template/--not-template", default=None, help="Mark project as template or not")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def projects_template(ctx, project_id, is_template, use_json):
    """Set or unset a project as a template."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data: dict = {}
    if is_template is not None:
        data["isTemplate"] = is_template
    result = b.update_project_template(ws, project_id, data)
    _out(ctx, result, lambda _: repl_skin.success(f"Updated template for project {project_id}"))


# ── projects extra commands ────────────────────────────────────────────

@projects.command("add-members")
@click.argument("project_id")
@click.option("--user-id", "user_ids", multiple=True, required=True,
              help="User ID to add (repeatable)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def projects_add_members(ctx, project_id, user_ids, use_json):
    """Add members to a project."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.assign_project_members(ws, project_id, {
        "memberships": [{"userId": uid} for uid in user_ids]
    })
    _out(ctx, data, lambda _: repl_skin.success(f"Members added to project {project_id}."))


@projects.command("user-cost-rate")
@click.argument("project_id")
@click.argument("user_id")
@click.option("--amount", required=True, type=int, help="Rate amount in cents (integer)")
@click.option("--since", default=None, help="Effective date (ISO datetime)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def projects_user_cost_rate(ctx, project_id, user_id, amount, since, use_json):
    """Set a user's cost rate on a project."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"amount": amount}
    if since is not None:
        body["since"] = since
    data = b.update_project_user_cost_rate(ws, project_id, user_id, body)
    _out(ctx, data, lambda _: repl_skin.success(
        f"Cost rate updated for user {user_id} on project {project_id}."))


@projects.command("user-hourly-rate")
@click.argument("project_id")
@click.argument("user_id")
@click.option("--amount", required=True, type=int, help="Rate amount in cents (integer)")
@click.option("--since", default=None, help="Effective date (ISO datetime)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def projects_user_hourly_rate(ctx, project_id, user_id, amount, since, use_json):
    """Set a user's hourly rate on a project."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"amount": amount}
    if since is not None:
        body["since"] = since
    data = b.update_project_user_hourly_rate(ws, project_id, user_id, body)
    _out(ctx, data, lambda _: repl_skin.success(
        f"Hourly rate updated for user {user_id} on project {project_id}."))
