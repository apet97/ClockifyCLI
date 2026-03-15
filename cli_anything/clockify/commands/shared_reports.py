from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils import repl_skin
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, handle_errors,
)


# ── shared-reports ────────────────────────────────────────────────────

@click.group("shared-reports")
def shared_reports():
    """Shared report management."""
    pass


@shared_reports.command("list")
@click.option("--filter", "shared_reports_filter", default=None,
              type=click.Choice(["ALL", "CREATED_BY_ME", "SHARED_WITH_ME"]),
              help="Filter shared reports by origin")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def shared_reports_list(ctx, shared_reports_filter, limit, use_json):
    """List shared reports."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_shared_reports(ws, shared_reports_filter=shared_reports_filter or None)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_shared_reports)


@shared_reports.command("get")
@click.argument("report_id")
@click.option("--start", default=None, help="Date range start (ISO datetime)")
@click.option("--end", default=None, help="Date range end (ISO datetime)")
@click.option("--sort-column", default=None, help="Sort column")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--export-type", "export_type", default=None,
              type=click.Choice(["JSON", "JSON_V1", "PDF", "CSV", "XLSX", "ZIP"]),
              help="Export format")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def shared_reports_get(ctx, report_id, start, end, sort_column, sort_order, export_type, page, page_size, use_json):
    """Get a shared report by ID."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    data = b.get_shared_report(report_id,
                               date_range_start=start,
                               date_range_end=end,
                               sort_column=sort_column,
                               sort_order=sort_order,
                               export_type=export_type,
                               page=page,
                               page_size=page_size)
    _out(ctx, data)


@shared_reports.command("get-public")
@click.argument("report_id")
@click.option("--start", "date_range_start", default=None, help="Date range start (ISO datetime)")
@click.option("--end", "date_range_end", default=None, help="Date range end (ISO datetime)")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--sort-column", default=None, help="Sort column")
@click.option("--export-type", "export_type", default=None,
              type=click.Choice(["JSON", "JSON_V1", "PDF", "CSV", "XLSX", "ZIP"]),
              help="Export format")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def shared_reports_get_public(ctx, report_id, date_range_start, date_range_end, sort_order, sort_column, export_type, page, page_size, use_json):
    """Get a public shared report by ID (reports domain)."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    data = b.get_public_shared_report(
        report_id,
        dateRangeStart=date_range_start,
        dateRangeEnd=date_range_end,
        sortOrder=sort_order,
        sortColumn=sort_column,
        exportType=export_type,
        page=page,
        page_size=page_size,
    )
    _out(ctx, data)


_SHARED_REPORT_TYPES = [
    "DETAILED", "WEEKLY", "SUMMARY", "SCHEDULED", "EXPENSE_DETAILED",
    "EXPENSE_RECEIPT", "PTO_REQUESTS", "PTO_BALANCE", "ATTENDANCE",
    "INVOICE_EXPENSE", "INVOICE_TIME", "PROJECT", "TEAM_FULL",
    "TEAM_LIMITED", "TEAM_GROUPS", "INVOICES", "KIOSK_PIN_LIST",
    "KIOSK_ASSIGNEES",
]

@shared_reports.command("create")
@click.argument("name")
@click.option("--public", is_flag=True, default=False)
@click.option("--type", "report_type", default=None,
              type=click.Choice(_SHARED_REPORT_TYPES),
              help="Shared report type")
@click.option("--fixed-date/--no-fixed-date", "fixed_date", default=None, help="Use fixed date range")
@click.option("--visible-to-user", "visible_to_users", multiple=True, help="User ID with access (repeatable)")
@click.option("--visible-to-group", "visible_to_groups", multiple=True, help="User group ID with access (repeatable)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def shared_reports_create(ctx, name, public, report_type, fixed_date, visible_to_users, visible_to_groups, use_json):
    """Create a shared report."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"name": name, "isPublic": public}
    if report_type:
        body["type"] = report_type
    if fixed_date is not None:
        body["fixedDate"] = fixed_date
    if visible_to_users:
        body["visibleToUsers"] = list(visible_to_users)
    if visible_to_groups:
        body["visibleToUserGroups"] = list(visible_to_groups)
    data = b.create_shared_report(ws, body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Shared report created: {d.get('name', '')} [{d.get('id', '')}]"
    ))


@shared_reports.command("update")
@click.argument("report_id")
@click.option("--name", default=None, help="New name")
@click.option("--public/--private", "is_public", default=None, help="Make report public or private")
@click.option("--fixed-date/--no-fixed-date", "fixed_date", default=None, help="Use fixed date range")
@click.option("--visible-to-user", "visible_to_users", multiple=True, help="User ID with access (repeatable)")
@click.option("--visible-to-group", "visible_to_groups", multiple=True, help="User group ID with access (repeatable)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def shared_reports_update(ctx, report_id, name, is_public, fixed_date, visible_to_users, visible_to_groups, use_json):
    """Update a shared report."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data: dict = {}
    if name is not None:
        data["name"] = name
    if is_public is not None:
        data["isPublic"] = is_public
    if fixed_date is not None:
        data["fixedDate"] = fixed_date
    if visible_to_users:
        data["visibleToUsers"] = list(visible_to_users)
    if visible_to_groups:
        data["visibleToUserGroups"] = list(visible_to_groups)
    result = b.update_shared_report(ws, report_id, data)
    _out(ctx, result, lambda _: repl_skin.success(f"Updated shared report {report_id}"))


@shared_reports.command("delete")
@click.argument("report_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def shared_reports_delete(ctx, report_id, confirm, use_json):
    """Delete a shared report."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"shared report {report_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_shared_report(ws, report_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Shared report {report_id} deleted."))
