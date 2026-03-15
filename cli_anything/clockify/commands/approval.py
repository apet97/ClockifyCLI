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

# ── approval ──────────────────────────────────────────────────────────

@click.group()
def approval():
    """Approval request management."""
    pass


@approval.command("list")
@click.option("--status", default=None,
              type=click.Choice(["PENDING", "APPROVED", "WITHDRAWN_APPROVAL"]),
              help="Filter by approval status")
@click.option("--sort-column", default=None,
              type=click.Choice(["ID", "USER_ID", "START", "UPDATED_AT"]),
              help="Sort column")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", default=None, type=int, help="Results per page")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def approval_list(ctx, status, sort_column, sort_order, page, page_size, limit, use_json):
    """List approval requests."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_approvals(ws, status=status or None, sort_column=sort_column or None, sort_order=sort_order or None, page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_approvals)


@approval.command("submit")
@click.option("--start", required=True, help="Period start date (YYYY-MM-DD)")
@click.option("--period", default=None,
              type=click.Choice(["WEEKLY", "SEMI_MONTHLY", "MONTHLY"]),
              help="Approval period type (must match workspace setting)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def approval_submit(ctx, start, period, use_json):
    """Submit entries for approval."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    start_iso = parse_date_arg(start) + "T00:00:00Z"
    body: dict = {"periodStart": start_iso}
    if period:
        body["period"] = period
    data = b.submit_approval(ws, body)
    _out(ctx, data, lambda _: repl_skin.success("Approval request submitted."))


@approval.command("update")
@click.argument("approval_id")
@click.option("--state", required=True,
              type=click.Choice(["PENDING", "APPROVED", "WITHDRAWN_SUBMISSION",
                                 "WITHDRAWN_APPROVAL", "REJECTED"]),
              help="New approval state")
@click.option("--note", default=None, help="Approval note (max 3000 chars)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def approval_update(ctx, approval_id, state, note, use_json):
    """Approve, reject, or withdraw an approval request."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"state": state}
    if note is not None:
        body["note"] = note
    data = b.update_approval(ws, approval_id, body)
    _out(ctx, data, lambda _: repl_skin.success(f"Approval {approval_id} → {state}."))


@approval.command("submit-for-user")
@click.argument("user_id")
@click.option("--start", required=True, help="Period start date (YYYY-MM-DD)")
@click.option("--period", default=None,
              type=click.Choice(["WEEKLY", "SEMI_MONTHLY", "MONTHLY"]),
              help="Approval period type")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def approval_submit_for_user(ctx, user_id, start, period, use_json):
    """Submit approval request for a specific user."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"periodStart": parse_date_arg(start) + "T00:00:00Z"}
    if period:
        body["period"] = period
    result = b.submit_approval_for_user(ws, user_id, body)
    _out(ctx, result, lambda _: repl_skin.success(f"Submitted approval for user {user_id}"))


@approval.command("resubmit")
@click.option("--start", required=True, help="Period start date (YYYY-MM-DD)")
@click.option("--period", default=None,
              type=click.Choice(["WEEKLY", "SEMI_MONTHLY", "MONTHLY"]),
              help="Approval period type")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def approval_resubmit(ctx, start, period, use_json):
    """Resubmit a rejected approval request."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"periodStart": parse_date_arg(start) + "T00:00:00Z"}
    if period:
        body["period"] = period
    result = b.resubmit_approval(ws, body)
    _out(ctx, result, lambda _: repl_skin.success("Approval resubmitted."))


# ── approval extra commands ────────────────────────────────────────────

@approval.command("resubmit-for-user")
@click.argument("user_id")
@click.option("--start", required=True, help="Period start date (YYYY-MM-DD)")
@click.option("--period", default=None,
              type=click.Choice(["WEEKLY", "SEMI_MONTHLY", "MONTHLY"]),
              help="Approval period type")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def approval_resubmit_for_user(ctx, user_id, start, period, use_json):
    """Resubmit entries for approval for a specific user."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"periodStart": parse_date_arg(start) + "T00:00:00Z"}
    if period:
        body["period"] = period
    result = b.resubmit_approval_for_user(ws, user_id, body)
    _out(ctx, result, lambda _: repl_skin.success(
        f"Entries resubmitted for approval for user {user_id}."))
