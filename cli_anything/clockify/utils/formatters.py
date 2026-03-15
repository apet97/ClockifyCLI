"""Output formatting helpers for the Clockify CLI.

Provides table and JSON output for all resource types.
"""

from __future__ import annotations

import json
from typing import Any

import click

try:
    from tabulate import tabulate as _tabulate_fn
    _HAS_TABULATE = True
except ImportError:
    _tabulate_fn = None  # type: ignore[assignment]
    _HAS_TABULATE = False

from cli_anything.clockify.utils.time_utils import (
    format_duration_hms,
    parse_duration_iso,
    elapsed_since,
)


def print_json(data: Any) -> None:
    """Print data as pretty-printed JSON."""
    click.echo(json.dumps(data, indent=2, default=str))


def _table(headers: list[str], rows: list[list[str]], fmt: str = "simple") -> str:
    if _HAS_TABULATE and _tabulate_fn is not None:
        return _tabulate_fn(rows, headers=headers, tablefmt=fmt)
    # Fallback: basic formatting
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    fmt_row = "  ".join(f"{{:<{w}}}" for w in col_widths)
    lines = [fmt_row.format(*headers)]
    lines.append("  ".join("-" * w for w in col_widths))
    for row in rows:
        padded = [str(row[i]) if i < len(row) else "" for i in range(len(headers))]
        lines.append(fmt_row.format(*padded))
    return "\n".join(lines)


def print_workspaces(workspaces: list[dict]) -> None:
    headers = ["ID", "Name", "Currency"]
    rows = [
        [w.get("id", ""), w.get("name", ""), w.get("currency", {}).get("code", "")]
        for w in workspaces
    ]
    click.echo(_table(headers, rows))


def print_projects(projects: list[dict]) -> None:
    headers = ["ID", "Name", "Client", "Color", "Archived"]
    rows = [
        [
            p.get("id", ""),
            p.get("name", ""),
            p.get("clientName", "") or p.get("client", {}).get("name", "") if isinstance(p.get("client"), dict) else p.get("clientName", ""),
            p.get("color", ""),
            str(p.get("archived", False)),
        ]
        for p in projects
    ]
    click.echo(_table(headers, rows))


def print_clients(clients: list[dict]) -> None:
    headers = ["ID", "Name"]
    rows = [[c.get("id", ""), c.get("name", "")] for c in clients]
    click.echo(_table(headers, rows))


def print_tags(tags: list[dict]) -> None:
    headers = ["ID", "Name"]
    rows = [[t.get("id", ""), t.get("name", "")] for t in tags]
    click.echo(_table(headers, rows))


def print_tasks(tasks: list[dict]) -> None:
    headers = ["ID", "Name", "Status", "Duration"]
    rows = [
        [
            t.get("id", ""),
            t.get("name", ""),
            t.get("status", ""),
            format_duration_hms(parse_duration_iso(t.get("duration") or "PT0S")),
        ]
        for t in tasks
    ]
    click.echo(_table(headers, rows))


def print_users(users: list[dict]) -> None:
    headers = ["ID", "Name", "Email", "Status"]
    rows = [
        [
            u.get("id", ""),
            u.get("name", ""),
            u.get("email", ""),
            u.get("status", ""),
        ]
        for u in users
    ]
    click.echo(_table(headers, rows))


def print_entries(entries: list[dict]) -> None:
    headers = ["ID", "Date", "Duration", "Project", "Description"]
    rows = []
    for e in entries:
        ti = e.get("timeInterval", {})
        start = ti.get("start", "")[:10] if ti.get("start") else ""
        dur_iso = ti.get("duration", "PT0S") or "PT0S"
        dur = format_duration_hms(parse_duration_iso(dur_iso))
        proj = e.get("projectName", "") or (
            e.get("project", {}).get("name", "") if isinstance(e.get("project"), dict) else ""
        )
        desc = e.get("description", "")
        rows.append([e.get("id", ""), start, dur, proj, desc])
    click.echo(_table(headers, rows))


def print_timer(entry: dict | None, *, running: bool) -> None:
    if not running or not entry:
        click.echo("No timer running.")
        return
    ti = entry.get("timeInterval", {})
    start_iso = ti.get("start", "")
    elapsed = elapsed_since(start_iso) if start_iso else "?"
    proj = entry.get("projectName", "") or ""
    desc = entry.get("description", "")
    click.echo(f"Running  {elapsed}  {proj}  {desc}")


def print_report_summary(data: dict) -> None:
    """Print summary report totals."""
    groups = data.get("groupOne", [])
    headers = ["Name", "Duration"]
    rows = []
    for g in groups:
        name = g.get("name", "")
        dur = format_duration_hms(g.get("duration") or 0)
        rows.append([name, dur])
    totals = data.get("totals", [{}])
    total_dur = (totals[0].get("totalTime") or 0) if totals else 0
    click.echo(_table(headers, rows))
    click.echo(f"\nTotal: {format_duration_hms(total_dur)}")


def print_webhooks(webhooks: list[dict]) -> None:
    headers = ["ID", "Name", "URL", "Trigger"]
    rows = [
        [
            w.get("id", ""),
            w.get("name", ""),
            w.get("url", ""),
            w.get("triggerSourceType", ""),
        ]
        for w in webhooks
    ]
    click.echo(_table(headers, rows))


def print_approvals(approvals: list[dict]) -> None:
    headers = ["ID", "Status", "Owner", "Period"]
    rows = [
        [
            a.get("id", ""),
            a.get("status", ""),
            a.get("ownerId", ""),
            f"{(a.get('dateRangeStart') or '')[:10]} – {(a.get('dateRangeEnd') or '')[:10]}",
        ]
        for a in approvals
    ]
    click.echo(_table(headers, rows))


def print_groups(groups: list[dict]) -> None:
    headers = ["ID", "Name", "Members"]
    rows = [
        [
            g.get("id", ""),
            g.get("name", ""),
            str(len(g.get("userIds") or [])),
        ]
        for g in groups
    ]
    click.echo(_table(headers, rows))


def print_expenses(expenses: list[dict]) -> None:
    headers = ["ID", "Date", "Amount", "Category", "Note"]
    rows = [
        [
            e.get("id", ""),
            (e.get("date") or "")[:10],
            str((e.get("total") or {}).get("amount", "") if isinstance(e.get("total"), dict) else (e.get("amount") or "")),
            (e.get("categoryName") or ((e.get("category") or {}).get("name", "") if isinstance(e.get("category"), dict) else "")),
            e.get("notes", "") or e.get("note", ""),
        ]
        for e in expenses
    ]
    click.echo(_table(headers, rows))


def print_expense_categories(categories: list[dict]) -> None:
    headers = ["ID", "Name", "Unit"]
    rows = [
        [
            c.get("id", ""),
            c.get("name", ""),
            c.get("unit", ""),
        ]
        for c in categories
    ]
    click.echo(_table(headers, rows))


def print_holidays(holidays: list[dict]) -> None:
    headers = ["ID", "Name", "Date", "Recurring"]
    rows = [
        [
            h.get("id", ""),
            h.get("name", ""),
            h.get("date", "")[:10] if h.get("date") else "",
            str(h.get("recurring", False)),
        ]
        for h in holidays
    ]
    click.echo(_table(headers, rows))


def print_invoices(invoices: list[dict]) -> None:
    headers = ["ID", "Number", "Status", "Client", "Amount"]
    rows = [
        [
            inv.get("id", ""),
            inv.get("invoiceNumber", ""),
            inv.get("status", ""),
            inv.get("clientName", ""),
            str(inv.get("total") or ""),
        ]
        for inv in invoices
    ]
    click.echo(_table(headers, rows))


def print_invoice_payments(payments: list[dict]) -> None:
    headers = ["ID", "Date", "Amount", "Note"]
    rows = [
        [
            p.get("id", ""),
            p.get("date", "")[:10] if p.get("date") else "",
            str(p.get("amount") or ""),
            p.get("note", ""),
        ]
        for p in payments
    ]
    click.echo(_table(headers, rows))


def print_time_off_policies(policies: list[dict]) -> None:
    headers = ["ID", "Name", "Type", "Active"]
    rows = [
        [
            p.get("id", ""),
            p.get("name", ""),
            p.get("timeOffType", ""),
            str(p.get("isActive", True)),
        ]
        for p in policies
    ]
    click.echo(_table(headers, rows))


def print_custom_fields(fields: list[dict]) -> None:
    headers = ["ID", "Name", "Type", "Status"]
    rows = [
        [
            f.get("id", ""),
            f.get("name", ""),
            f.get("type", ""),
            f.get("status", ""),
        ]
        for f in fields
    ]
    click.echo(_table(headers, rows))


def print_shared_reports(reports: list[dict]) -> None:
    headers = ["ID", "Name", "Public"]
    rows = [
        [
            r.get("id", ""),
            r.get("name", ""),
            str(r.get("isPublic", False)),
        ]
        for r in reports
    ]
    click.echo(_table(headers, rows))


def print_entity_changes(changes: list[dict]) -> None:
    headers = ["ID", "Type", "Changed At"]
    rows = [
        [
            c.get("id", ""),
            c.get("entityType", ""),
            c.get("changedAt", "")[:19] if c.get("changedAt") else "",
        ]
        for c in changes
    ]
    click.echo(_table(headers, rows))


def print_assignments(assignments: list) -> None:
    """Print scheduling assignments in tabular format."""
    if not assignments:
        click.echo("No assignments found.")
        return
    headers = ["ID", "Project", "User", "Start", "End", "Hours"]
    rows = []
    for a in assignments:
        rows.append([
            (a.get("id") or "")[:8] + "...",
            (a.get("projectName") or a.get("projectId") or "")[:20],
            (a.get("userName") or a.get("userId") or "")[:20],
            (a.get("start") or "")[:10],
            (a.get("end") or "")[:10],
            str(a.get("totalBillableHours") or a.get("hours") or ""),
        ])
    col_widths = [max(len(str(r[i])) for r in ([headers] + rows)) for i in range(len(headers))]
    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)
    click.echo(fmt.format(*headers))
    click.echo("  ".join("-" * w for w in col_widths))
    for row in rows:
        click.echo(fmt.format(*row))


def print_scheduling_totals(data: dict) -> None:
    """Print scheduling capacity/totals summary."""
    if not data:
        click.echo("No data.")
        return
    for key, value in data.items():
        if isinstance(value, dict):
            click.echo(f"{key}:")
            for k, v in value.items():
                click.echo(f"  {k}: {v}")
        else:
            click.echo(f"{key}: {value}")
