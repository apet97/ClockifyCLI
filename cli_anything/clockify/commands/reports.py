from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils.time_utils import parse_date_arg
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, handle_errors,
)


# ── reports ───────────────────────────────────────────────────────────

@click.group()
def reports():
    """Reporting commands."""
    pass


@reports.command("detailed")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD or 'today')")
@click.option("--end", required=True, help="End date (YYYY-MM-DD or 'today')")
@click.option("--project", default=None, help="Filter by project ID")
@click.option("--user", "user_ids", multiple=True, help="Filter by user ID (repeatable)")
@click.option("--client", "client_ids", multiple=True, help="Filter by client ID (repeatable)")
@click.option("--tag", "tag_ids", multiple=True, help="Filter by tag ID (repeatable)")
@click.option("--task", "task_ids", multiple=True, help="Filter by task ID (repeatable)")
@click.option("--user-group", "user_group_ids", multiple=True, help="Filter by user group ID (repeatable)")
@click.option("--billable/--no-billable", default=None, help="Filter by billable status")
@click.option("--description", default=None, help="Filter by description text")
@click.option("--approval-state", default=None,
              type=click.Choice(["APPROVED", "UNAPPROVED", "ALL"]),
              help="Filter by approval state")
@click.option("--invoicing-state", default=None,
              type=click.Choice(["INVOICED", "UNINVOICED", "ALL"]),
              help="Filter by invoicing state")
@click.option("--sort-column", "detail_sort_column", default=None,
              type=click.Choice(["ID", "DESCRIPTION", "USER", "DURATION", "DATE",
                                 "ZONED_DATE", "NATURAL", "USER_DATE"]),
              help="Sort column for detailed report")
@click.option("--sort-order", "detail_sort_order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--export-type", default=None,
              type=click.Choice(["JSON", "JSON_V1", "PDF", "CSV", "XLSX", "ZIP"]),
              help="Export format")
@click.option("--archived", is_flag=True, default=False, help="Include archived entries")
@click.option("--amount-shown", default=None,
              type=click.Choice(["EARNED", "COST", "PROFIT", "HIDE_AMOUNT"]),
              help="Amount display mode")
@click.option("--rounding", is_flag=True, default=False, help="Round durations")
@click.option("--timezone", default=None, help="Timezone for report (e.g. UTC, America/New_York)")
@click.option("--page", default=1, type=int)
@click.option("--page-size", default=50, type=int)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def reports_detailed(ctx, start, end, project, user_ids, client_ids, tag_ids, task_ids, user_group_ids, billable, description, approval_state, invoicing_state, detail_sort_column, detail_sort_order, export_type, archived, amount_shown, rounding, timezone, page, page_size, use_json):
    """Detailed time report."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    start_iso = parse_date_arg(start) + "T00:00:00Z"
    end_iso = parse_date_arg(end) + "T23:59:59Z"
    project_ids = [project] if project else None
    data = b.report_detailed(
        ws, start_iso, end_iso,
        project_ids=project_ids, user_ids=list(user_ids) if user_ids else None,
        client_ids=list(client_ids) if client_ids else None,
        tag_ids=list(tag_ids) if tag_ids else None,
        billable=billable,
        description=description or None,
        approval_state=approval_state or None,
        invoicing_state=invoicing_state or None,
        sort_column=detail_sort_column or None,
        sort_order=detail_sort_order or None,
        export_type=export_type or None,
        page=page, page_size=page_size,
        task_ids=list(task_ids) if task_ids else None,
        user_group_ids=list(user_group_ids) if user_group_ids else None,
        archived=True if archived else None,
        amount_shown=amount_shown or None,
        rounding=True if rounding else None,
        timezone=timezone or None,
    )
    _out(ctx, data)


@reports.command("summary")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD or 'today')")
@click.option("--end", required=True, help="End date (YYYY-MM-DD or 'today')")
@click.option("--group-by", default="PROJECT",
              type=click.Choice(["PROJECT", "CLIENT", "TAG", "TASK", "USER",
                                 "DATE", "WEEK", "MONTH", "USER_GROUP", "TIMEENTRY"]),
              help="Group results by")
@click.option("--sort-column", "summary_sort_column", default=None,
              type=click.Choice(["GROUP", "DURATION", "AMOUNT", "EARNED", "COST", "PROFIT"]),
              help="Sort column for summary report")
@click.option("--sort-order", "summary_sort_order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--billable/--no-billable", default=None, help="Filter by billable status")
@click.option("--project", default=None, help="Filter by project ID")
@click.option("--user", "user_ids", multiple=True, help="Filter by user ID (repeatable)")
@click.option("--client", "client_ids", multiple=True, help="Filter by client ID (repeatable)")
@click.option("--tag", "tag_ids", multiple=True, help="Filter by tag ID (repeatable)")
@click.option("--task", "task_ids", multiple=True, help="Filter by task ID (repeatable)")
@click.option("--user-group", "user_group_ids", multiple=True, help="Filter by user group ID (repeatable)")
@click.option("--description", default=None, help="Filter by description text")
@click.option("--approval-state", default=None,
              type=click.Choice(["PENDING", "APPROVED", "WITHDRAWN_APPROVAL"]),
              help="Filter by approval state")
@click.option("--invoicing-state", default=None,
              type=click.Choice(["INVOICED", "UNINVOICED"]),
              help="Filter by invoicing state")
@click.option("--export-type", default=None,
              type=click.Choice(["JSON", "JSON_V1", "PDF", "CSV", "XLSX", "ZIP"]),
              help="Export format")
@click.option("--archived", is_flag=True, default=False, help="Include archived entries")
@click.option("--amount-shown", default=None,
              type=click.Choice(["EARNED", "COST", "PROFIT", "HIDE_AMOUNT"]),
              help="Amount display mode")
@click.option("--rounding", is_flag=True, default=False, help="Round durations")
@click.option("--timezone", default=None, help="Timezone for report (e.g. UTC, America/New_York)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def reports_summary(ctx, start, end, group_by, summary_sort_column, summary_sort_order, billable, project, user_ids, client_ids, tag_ids, task_ids, user_group_ids, description, approval_state, invoicing_state, export_type, archived, amount_shown, rounding, timezone, use_json):
    """Summary time report."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    start_iso = parse_date_arg(start) + "T00:00:00Z"
    end_iso = parse_date_arg(end) + "T23:59:59Z"
    data = b.report_summary(
        ws, start_iso, end_iso, group_by=group_by,
        sort_column=summary_sort_column or None,
        billable=billable,
        project_ids=[project] if project else None,
        user_ids=list(user_ids) if user_ids else None,
        client_ids=list(client_ids) if client_ids else None,
        tag_ids=list(tag_ids) if tag_ids else None,
        description=description or None,
        approval_state=approval_state or None,
        invoicing_state=invoicing_state or None,
        export_type=export_type or None,
        sort_order=summary_sort_order or None,
        task_ids=list(task_ids) if task_ids else None,
        user_group_ids=list(user_group_ids) if user_group_ids else None,
        archived=True if archived else None,
        amount_shown=amount_shown or None,
        rounding=True if rounding else None,
        timezone=timezone or None,
    )
    _out(ctx, data, fmt.print_report_summary)


@reports.command("weekly")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD or 'today')")
@click.option("--end", required=True, help="End date (YYYY-MM-DD or 'today')")
@click.option("--group-by", default="USER",
              type=click.Choice(["PROJECT", "USER"]),
              help="Group by (default: USER)")
@click.option("--subgroup", default="TIME",
              type=click.Choice(["TIME"]),
              help="Subgroup (default: TIME)")
@click.option("--sort-order", "weekly_sort_order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--billable/--no-billable", default=None, help="Filter by billable status")
@click.option("--project", default=None, help="Filter by project ID")
@click.option("--user", "user_ids", multiple=True, help="Filter by user ID (repeatable)")
@click.option("--client", "client_ids", multiple=True, help="Filter by client ID (repeatable)")
@click.option("--tag", "tag_ids", multiple=True, help="Filter by tag ID (repeatable)")
@click.option("--task", "task_ids", multiple=True, help="Filter by task ID (repeatable)")
@click.option("--user-group", "user_group_ids", multiple=True, help="Filter by user group ID (repeatable)")
@click.option("--description", default=None, help="Filter by description text")
@click.option("--approval-state", default=None,
              type=click.Choice(["PENDING", "APPROVED", "WITHDRAWN_APPROVAL"]),
              help="Filter by approval state")
@click.option("--invoicing-state", default=None,
              type=click.Choice(["INVOICED", "UNINVOICED"]),
              help="Filter by invoicing state")
@click.option("--export-type", default=None,
              type=click.Choice(["JSON", "JSON_V1", "PDF", "CSV", "XLSX", "ZIP"]),
              help="Export format")
@click.option("--archived", is_flag=True, default=False, help="Include archived entries")
@click.option("--amount-shown", default=None,
              type=click.Choice(["EARNED", "COST", "PROFIT", "HIDE_AMOUNT"]),
              help="Amount display mode")
@click.option("--rounding", is_flag=True, default=False, help="Round durations")
@click.option("--timezone", default=None, help="Timezone for report (e.g. UTC, America/New_York)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def reports_weekly(ctx, start, end, group_by, subgroup, weekly_sort_order, billable, project, user_ids, client_ids, tag_ids, task_ids, user_group_ids, description, approval_state, invoicing_state, export_type, archived, amount_shown, rounding, timezone, use_json):
    """Weekly time report."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    start_iso = parse_date_arg(start) + "T00:00:00Z"
    end_iso = parse_date_arg(end) + "T23:59:59Z"
    data = b.report_weekly(
        ws, start_iso, end_iso,
        group=group_by, subgroup=subgroup,
        billable=billable,
        project_ids=[project] if project else None,
        user_ids=list(user_ids) if user_ids else None,
        client_ids=list(client_ids) if client_ids else None,
        tag_ids=list(tag_ids) if tag_ids else None,
        description=description or None,
        approval_state=approval_state or None,
        invoicing_state=invoicing_state or None,
        export_type=export_type or None,
        sort_order=weekly_sort_order or None,
        task_ids=list(task_ids) if task_ids else None,
        user_group_ids=list(user_group_ids) if user_group_ids else None,
        archived=True if archived else None,
        amount_shown=amount_shown or None,
        rounding=True if rounding else None,
        timezone=timezone or None,
    )
    _out(ctx, data)


# ── reports (additional commands) ─────────────────────────────────────

@reports.command("attendance")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD)")
@click.option("--user", "user_ids", multiple=True, help="Filter by user ID (repeatable)")
@click.option("--user-group", "user_group_ids", multiple=True, help="Filter by user group ID (repeatable)")
@click.option("--project", "project_ids", multiple=True, help="Filter by project ID (repeatable)")
@click.option("--client", "client_ids", multiple=True, help="Filter by client ID (repeatable)")
@click.option("--tag", "tag_ids", multiple=True, help="Filter by tag ID (repeatable)")
@click.option("--task", "task_ids", multiple=True, help="Filter by task ID (repeatable)")
@click.option("--description", default=None, help="Filter by description text")
@click.option("--approval-state", default=None,
              type=click.Choice(["APPROVED", "UNAPPROVED", "ALL"]),
              help="Filter by approval state")
@click.option("--billable/--no-billable", default=None, help="Filter by billable status")
@click.option("--sort-column", default=None,
              type=click.Choice(["USER", "DATE", "START", "END", "BREAK", "WORK", "CAPACITY", "OVERTIME", "TIME_OFF"]),
              help="Attendance sort column")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--export-type", "export_type", default=None,
              type=click.Choice(["JSON", "JSON_V1", "PDF", "CSV", "XLSX", "ZIP"]),
              help="Export format")
@click.option("--archived", is_flag=True, default=False, help="Include archived entries")
@click.option("--rounding", is_flag=True, default=False, help="Round durations")
@click.option("--timezone", default=None, help="Timezone for report (e.g. UTC, America/New_York)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def reports_attendance(ctx, start, end, user_ids, user_group_ids, project_ids, client_ids, tag_ids, task_ids, description, approval_state, billable, sort_column, sort_order, page, page_size, export_type, archived, rounding, timezone, use_json):
    """Attendance report."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    start_iso = parse_date_arg(start) + "T00:00:00Z"
    end_iso = parse_date_arg(end) + "T23:59:59Z"
    data = b.report_attendance(ws, start_iso, end_iso,
                                approval_state=approval_state,
                                billable=billable,
                                sort_column=sort_column,
                                sort_order=sort_order,
                                page=page,
                                page_size=page_size,
                                export_type=export_type,
                                user_ids=list(user_ids) if user_ids else None,
                                user_group_ids=list(user_group_ids) if user_group_ids else None,
                                project_ids=list(project_ids) if project_ids else None,
                                client_ids=list(client_ids) if client_ids else None,
                                tag_ids=list(tag_ids) if tag_ids else None,
                                task_ids=list(task_ids) if task_ids else None,
                                description=description or None,
                                archived=True if archived else None,
                                rounding=True if rounding else None,
                                timezone=timezone or None)
    _out(ctx, data)


@reports.command("expense")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD)")
@click.option("--user", "user_ids", multiple=True, help="Filter by user ID (repeatable)")
@click.option("--user-group", "user_group_ids", multiple=True, help="Filter by user group ID (repeatable)")
@click.option("--project", "project_ids", multiple=True, help="Filter by project ID (repeatable)")
@click.option("--client", "client_ids", multiple=True, help="Filter by client ID (repeatable)")
@click.option("--task", "task_ids", multiple=True, help="Filter by task ID (repeatable)")
@click.option("--category", "category_ids", multiple=True, help="Filter by expense category ID (repeatable)")
@click.option("--approval-state", default=None,
              type=click.Choice(["APPROVED", "UNAPPROVED", "ALL"]),
              help="Filter by approval state")
@click.option("--billable/--no-billable", default=None, help="Filter by billable status")
@click.option("--sort-column", default=None,
              type=click.Choice(["ID", "PROJECT", "USER", "CATEGORY", "DATE", "AMOUNT"]),
              help="Expense sort column")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--invoicing-state", default=None,
              type=click.Choice(["INVOICED", "UNINVOICED", "ALL"]),
              help="Filter by invoicing state")
@click.option("--export-type", "export_type", default=None,
              type=click.Choice(["JSON", "JSON_V1", "PDF", "CSV", "XLSX", "ZIP"]),
              help="Export format")
@click.option("--timezone", default=None, help="Timezone for report (e.g. UTC, America/New_York)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def reports_expense(ctx, start, end, user_ids, user_group_ids, project_ids, client_ids, task_ids, category_ids, approval_state, billable, sort_column, sort_order, page, page_size, invoicing_state, export_type, timezone, use_json):
    """Expense report."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    start_iso = parse_date_arg(start) + "T00:00:00Z"
    end_iso = parse_date_arg(end) + "T23:59:59Z"
    data = b.report_expense(ws, start_iso, end_iso,
                             approval_state=approval_state,
                             billable=billable,
                             sort_column=sort_column,
                             sort_order=sort_order,
                             page=page,
                             page_size=page_size,
                             invoicing_state=invoicing_state,
                             export_type=export_type,
                             user_ids=list(user_ids) if user_ids else None,
                             user_group_ids=list(user_group_ids) if user_group_ids else None,
                             project_ids=list(project_ids) if project_ids else None,
                             client_ids=list(client_ids) if client_ids else None,
                             task_ids=list(task_ids) if task_ids else None,
                             category_ids=list(category_ids) if category_ids else None,
                             timezone=timezone or None)
    _out(ctx, data)
