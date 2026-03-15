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
    _parse_json_option,
)


# ── time-off ──────────────────────────────────────────────────────────

@click.group("time-off")
def time_off():
    """Time off management."""
    pass


@time_off.group("policies")
def time_off_policies():
    """Time off policy management."""
    pass


@time_off_policies.command("list")
@click.option("--name", default=None, help="Filter by policy name")
@click.option("--status", default=None,
              type=click.Choice(["ACTIVE", "ARCHIVED", "ALL"]),
              help="Filter by status")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_policies_list(ctx, name, status, page, page_size, limit, use_json):
    """List time off policies."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_time_off_policies(ws, name=name or None, status=status or None,
                                     page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_time_off_policies)


@time_off_policies.command("get")
@click.argument("policy_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_policies_get(ctx, policy_id, use_json):
    """Get a time off policy by ID."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.get_time_off_policy(ws, policy_id)
    _out(ctx, data)


_TIME_OFF_ICONS = [
    "UMBRELLA", "SNOWFLAKE", "FAMILY", "PLANE", "STETHOSCOPE",
    "HEALTH_METRICS", "CHILDCARE", "LUGGAGE", "MONETIZATION", "CALENDAR",
]


@time_off_policies.command("create")
@click.option("--name", required=True, help="Policy name")
@click.option("--type", "policy_type", default="VACATION", help="Policy type")
@click.option("--icon", default=None,
              type=click.Choice(_TIME_OFF_ICONS),
              help="Policy icon")
@click.option("--color", default=None, help="Color hex code (e.g. #8BC34A)")
@click.option("--allow-half-day/--no-half-day", "allow_half_day", default=None, help="Allow half-day requests")
@click.option("--allow-negative-balance/--no-negative-balance", "allow_negative_balance", default=None, help="Allow negative balance")
@click.option("--time-unit", "time_unit", default=None,
              type=click.Choice(["DAYS", "HOURS"]),
              help="Time unit for the policy")
@click.option("--everyone/--not-everyone", "everyone_including_new", default=None, help="Apply to all users including new")
@click.option("--has-expiration/--no-expiration", "has_expiration", default=None, help="Policy has expiration")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_policies_create(ctx, name, policy_type, icon, color, allow_half_day, allow_negative_balance, time_unit, everyone_including_new, has_expiration, use_json):
    """Create a new time-off policy."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"name": name, "policyType": policy_type}
    if icon:
        body["icon"] = icon
    if color:
        body["color"] = color
    if allow_half_day is not None:
        body["allowHalfDay"] = allow_half_day
    if allow_negative_balance is not None:
        body["allowNegativeBalance"] = allow_negative_balance
    if time_unit:
        body["timeUnit"] = time_unit
    if everyone_including_new is not None:
        body["everyoneIncludingNew"] = everyone_including_new
    if has_expiration is not None:
        body["hasExpiration"] = has_expiration
    result = b.create_time_off_policy(ws, body)
    _out(ctx, result, lambda d: repl_skin.success(
        f"Created time-off policy: {d.get('id', result)}"
    ))


@time_off_policies.command("update")
@click.argument("policy_id")
@click.option("--name", default=None, help="New name")
@click.option("--icon", default=None,
              type=click.Choice(_TIME_OFF_ICONS),
              help="Policy icon")
@click.option("--color", default=None, help="Color hex code (e.g. #8BC34A)")
@click.option("--allow-half-day/--no-half-day", "allow_half_day", default=None, help="Allow half-day requests")
@click.option("--allow-negative-balance/--no-negative-balance", "allow_negative_balance", default=None, help="Allow negative balance")
@click.option("--time-unit", "time_unit", default=None,
              type=click.Choice(["DAYS", "HOURS"]),
              help="Time unit for the policy")
@click.option("--everyone/--not-everyone", "everyone_including_new", default=None, help="Apply to all users including new")
@click.option("--has-expiration/--no-expiration", "has_expiration", default=None, help="Policy has expiration")
@click.option("--archived/--not-archived", "archived", default=None, help="Archive or unarchive policy")
@click.option("--approve", default=None, help="Approval config as JSON (e.g. '{\"type\":\"MANAGER\"}')")
@click.option("--user", "users", multiple=True, help="User ID to include (repeatable)")
@click.option("--user-group", "user_groups", multiple=True, help="User group ID (repeatable)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_policies_update(ctx, policy_id, name, icon, color, allow_half_day, allow_negative_balance, time_unit, everyone_including_new, has_expiration, archived, approve, users, user_groups, use_json):
    """Update a time-off policy."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data: dict = {}
    if name is not None:
        data["name"] = name
    if icon is not None:
        data["icon"] = icon
    if color is not None:
        data["color"] = color
    if allow_half_day is not None:
        data["allowHalfDay"] = allow_half_day
    if allow_negative_balance is not None:
        data["allowNegativeBalance"] = allow_negative_balance
    if time_unit is not None:
        data["timeUnit"] = time_unit
    if everyone_including_new is not None:
        data["everyoneIncludingNew"] = everyone_including_new
    if has_expiration is not None:
        data["hasExpiration"] = has_expiration
    if archived is not None:
        data["archived"] = archived
    if approve is not None:
        data["approve"] = _parse_json_option(approve, "--approve")
    if users:
        data["users"] = list(users)
    if user_groups:
        data["userGroups"] = list(user_groups)
    result = b.update_time_off_policy(ws, policy_id, data)
    _out(ctx, result, lambda _: repl_skin.success(f"Updated time-off policy {policy_id}"))


@time_off_policies.command("delete")
@click.argument("policy_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_policies_delete(ctx, policy_id, confirm, use_json):
    """Delete a time off policy."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"policy {policy_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_time_off_policy(ws, policy_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Policy {policy_id} deleted."))


@time_off_policies.command("status")
@click.argument("policy_id")
@click.option("--status", required=True,
              type=click.Choice(["ACTIVE", "ARCHIVED", "ALL"]),
              help="New policy status")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_policies_status(ctx, policy_id, status, use_json):
    """Update a time-off policy's status (activate/archive)."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.update_time_off_policy_status(ws, policy_id, {"status": status})
    _out(ctx, data, lambda _: repl_skin.success(f"Policy {policy_id} status → {status}."))


@time_off.group("request")
def time_off_request():
    """Time off request management."""
    pass


@time_off_request.command("create")
@click.option("--policy-id", required=True, help="Time off policy ID")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD)")
@click.option("--note", default="")
@click.option("--half-day", is_flag=True, default=False, help="Mark as half-day request")
@click.option("--half-day-period", default=None,
              type=click.Choice(["FIRST_HALF", "SECOND_HALF", "NOT_DEFINED"]),
              help="Which half of the day")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_request_create(ctx, policy_id, start, end, note, half_day, half_day_period, use_json):
    """Create a time off request."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    time_off_period: dict = {
        "period": {
            "start": parse_date_arg(start) + "T00:00:00Z",
            "end": parse_date_arg(end) + "T23:59:59Z",
        }
    }
    if half_day:
        time_off_period["isHalfDay"] = True
    if half_day_period:
        time_off_period["halfDayPeriod"] = half_day_period
    body: dict = {"timeOffPeriod": time_off_period, "note": note}
    data = b.create_time_off_request(ws, policy_id, body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Time off request created [{d.get('id', '')}]"
    ))


@time_off.group("balance")
def time_off_balance():
    """Time off balance."""
    pass


@time_off_balance.command("get")
@click.argument("user_id")
@click.option("--sort", default=None,
              type=click.Choice(["USER", "POLICY", "USED", "BALANCE", "TOTAL"]),
              help="Sort by field")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", default=None, type=int, help="Results per page")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_balance_get(ctx, user_id, sort, sort_order, page, page_size, use_json):
    """Get a user's time off balance."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.get_time_off_balance(ws, user_id, sort=sort or None, sort_order=sort_order or None, page=page, page_size=page_size)
    _out(ctx, data)


# ── time-off extra commands ────────────────────────────────────────────

@time_off_request.command("delete")
@click.argument("policy_id")
@click.argument("request_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_request_delete(ctx, policy_id, request_id, confirm, use_json):
    """Delete a time off request."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"time off request {request_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_time_off_request(ws, policy_id, request_id)
    _out(ctx, data, lambda _: repl_skin.success(
        f"Time off request {request_id} deleted."))


@time_off_request.command("update")
@click.argument("policy_id")
@click.argument("request_id")
@click.option("--status", required=True,
              type=click.Choice(["APPROVED", "REJECTED"]))
@click.option("--note", default=None, help="Note for the status change (max 3000 chars)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_request_update(ctx, policy_id, request_id, status, note, use_json):
    """Update a time off request status (approve/reject)."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body = {"status": status}
    if note is not None:
        body["note"] = note
    data = b.update_time_off_request_status(ws, policy_id, request_id, body)
    _out(ctx, data, lambda _: repl_skin.success(
        f"Time off request {request_id} → {status}."))


@time_off_request.command("create-for-user")
@click.argument("policy_id")
@click.argument("user_id")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD)")
@click.option("--note", default=None, help="Request note")
@click.option("--half-day", is_flag=True, default=False, help="Mark as half-day request")
@click.option("--half-day-period", default=None,
              type=click.Choice(["FIRST_HALF", "SECOND_HALF", "NOT_DEFINED"]),
              help="Which half of the day")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_request_create_for_user(ctx, policy_id, user_id, start, end, note, half_day, half_day_period, use_json):
    """Create a time off request for a specific user."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    time_off_period: dict = {
        "period": {
            "start": parse_date_arg(start) + "T00:00:00Z",
            "end": parse_date_arg(end) + "T23:59:59Z",
        }
    }
    if half_day:
        time_off_period["isHalfDay"] = True
    if half_day_period:
        time_off_period["halfDayPeriod"] = half_day_period
    body: dict = {"timeOffPeriod": time_off_period}
    if note is not None:
        body["note"] = note
    data = b.create_time_off_request_for_user(ws, policy_id, user_id, body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Time off request created for user {user_id} [{d.get('id', '')}]"))


@time_off.group("requests")
def time_off_requests():
    """Workspace-wide time off request listing."""
    pass


@time_off_requests.command("list")
@click.option("--status", "statuses", multiple=True,
              help="Filter by status (repeatable, e.g. PENDING, APPROVED, REJECTED)")
@click.option("--user", "users", multiple=True, help="Filter by user ID (repeatable)")
@click.option("--user-group", "user_groups", multiple=True,
              help="Filter by user group ID (repeatable)")
@click.option("--start", default=None, help="Start date filter (YYYY-MM-DD)")
@click.option("--end", default=None, help="End date filter (YYYY-MM-DD)")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_requests_list(ctx, statuses, users, user_groups, start, end, page, page_size, use_json):
    """List all time off requests in the workspace."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {}
    if statuses:
        body["statuses"] = list(statuses)
    if users:
        body["users"] = list(users)
    if user_groups:
        body["userGroups"] = list(user_groups)
    if start:
        body["start"] = parse_date_arg(start) + "T00:00:00Z"
    if end:
        body["end"] = parse_date_arg(end) + "T23:59:59Z"
    if page is not None:
        body["page"] = page
    if page_size is not None:
        body["pageSize"] = page_size
    data = b.list_workspace_time_off_requests(ws, body)
    _out(ctx, data)


@time_off_balance.command("policy")
@click.argument("policy_id")
@click.option("--sort", default=None,
              type=click.Choice(["USER", "POLICY", "USED", "BALANCE", "TOTAL"]),
              help="Sort by field")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_balance_policy(ctx, policy_id, sort, sort_order, page, page_size, use_json):
    """Get balance for a time off policy."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.get_policy_balance(ws, policy_id, sort=sort or None, sort_order=sort_order or None,
                                 page=page, page_size=page_size)
    _out(ctx, data)


@time_off_balance.command("update-policy")
@click.argument("policy_id")
@click.option("--user-id", "user_ids", multiple=True, required=True,
              help="User ID to update balance for (repeatable, min 1)")
@click.option("--value", required=True, type=float,
              help="Balance value (-10000 to 10000)")
@click.option("--note", default=None, help="Reason for balance change (max 3000 chars)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def time_off_balance_update_policy(ctx, policy_id, user_ids, value, note, use_json):
    """Update balance for users in a time off policy."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"userIds": list(user_ids), "value": value}
    if note:
        body["note"] = note
    data = b.update_policy_balance(ws, policy_id, body)
    _out(ctx, data, lambda _: repl_skin.success(f"Policy {policy_id} balance updated."))
