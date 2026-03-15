from __future__ import annotations

import base64

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


# ── expenses ──────────────────────────────────────────────────────────

@click.group()
def expenses():
    """Expense management."""
    pass


@expenses.command("list")
@click.option("--user", default=None, help="Filter by user ID")
@click.option("--page", default=None, type=int, help="Page number (1-based)")
@click.option("--page-size", "page_size", default=None, type=int, help="Items per page")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def expenses_list(ctx, user, page, page_size, limit, use_json):
    """List expenses."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_expenses(ws, user_id=user, page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_expenses)


@expenses.command("get")
@click.argument("expense_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def expenses_get(ctx, expense_id, use_json):
    """Get an expense by ID."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.get_expense(ws, expense_id)
    _out(ctx, data)


@expenses.command("create")
@click.option("--category-id", required=True, help="Expense category ID (24-character Clockify object ID)")
@click.option("--amount", required=True, type=float, help="Decimal amount, e.g. 50.0")
@click.option("--date", required=True, help="Date (YYYY-MM-DD, 'today', or 'yesterday')")
@click.option("--note", default="", help="Note")
@click.option("--user-id", "user_id", default=None, help="User ID (defaults to current user)")
@click.option("--project-id", "project_id", default=None, help="Project ID (24-character Clockify object ID)")
@click.option("--task-id", "task_id", default=None, help="Task ID (24-character Clockify object ID)")
@click.option("--billable/--no-billable", default=None, help="Mark expense as billable")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def expenses_create(ctx, category_id, amount, date, note, user_id, project_id, task_id, billable, use_json):
    """Create an expense."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {
        "categoryId": category_id,
        "amount": amount,
        "date": parse_date_arg(date) + "T00:00:00Z",
        "notes": note,
    }
    if user_id:
        body["userId"] = user_id
    if project_id:
        body["projectId"] = project_id
    if task_id:
        body["taskId"] = task_id
    if billable is not None:
        body["billable"] = billable
    data = b.create_expense(ws, body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Expense created [{d.get('id', '')}]"
    ))


@expenses.command("delete")
@click.argument("expense_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def expenses_delete(ctx, expense_id, confirm, use_json):
    """Delete an expense."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"expense {expense_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_expense(ws, expense_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Expense {expense_id} deleted."))


@expenses.command("update")
@click.argument("expense_id")
@click.option("--amount", type=float, default=None, help="Decimal amount, e.g. 99.5")
@click.option("--notes", default=None, help="Notes (max 3000 chars)")
@click.option("--category-id", "category_id", default=None, help="Expense category ID")
@click.option("--date", default=None, help="Expense date (YYYY-MM-DD, 'today', or 'yesterday')")
@click.option("--user-id", "user_id", default=None, help="User ID")
@click.option("--project-id", "project_id", default=None, help="Project ID")
@click.option("--task-id", "task_id", default=None, help="Task ID")
@click.option("--billable/--no-billable", default=None, help="Set billable status")
@click.option("--change-field", "change_fields", multiple=True,
              type=click.Choice(["USER", "DATE", "PROJECT", "TASK", "CATEGORY", "NOTES", "AMOUNT", "BILLABLE", "FILE"]),
              help="Field that was changed (repeatable, required by API)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def expenses_update(ctx, expense_id, amount, notes, category_id, date, user_id, project_id, task_id, billable, change_fields, use_json):
    """Update an expense."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {}
    if amount is not None:
        body["amount"] = amount
    if notes is not None:
        body["notes"] = notes
    if category_id is not None:
        body["categoryId"] = category_id
    if date is not None:
        body["date"] = parse_date_arg(date) + "T00:00:00Z"
    if user_id is not None:
        body["userId"] = user_id
    if project_id is not None:
        body["projectId"] = project_id
    if task_id is not None:
        body["taskId"] = task_id
    if billable is not None:
        body["billable"] = billable
    if change_fields:
        body["changeFields"] = list(change_fields)
    result = b.update_expense(ws, expense_id, body)
    _out(ctx, result, lambda _: repl_skin.success(f"Updated expense {expense_id}"))


@expenses.group("categories")
def expense_categories():
    """Expense category management."""
    pass


@expense_categories.command("list")
@click.option("--name", default=None, help="Filter by name")
@click.option("--archived", is_flag=True, default=False, help="Include archived categories")
@click.option("--sort-column", default=None,
              type=click.Choice(["NAME"]),
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
def expense_categories_list(ctx, name, archived, sort_column, sort_order, page, page_size, limit, use_json):
    """List expense categories."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_expense_categories(ws, name=name or None, archived=True if archived else None, sort_column=sort_column or None, sort_order=sort_order or None, page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_expense_categories)


@expense_categories.command("create")
@click.argument("name")
@click.option("--has-unit-price/--no-unit-price", "has_unit_price", default=None,
              help="Whether category has a unit price")
@click.option("--price-in-cents", "price_in_cents", default=None, type=int,
              help="Price in cents")
@click.option("--unit", default=None, help="Unit label (e.g. 'mile', 'km')")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def expense_categories_create(ctx, name, has_unit_price, price_in_cents, unit, use_json):
    """Create an expense category."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"name": name}
    if has_unit_price is not None:
        body["hasUnitPrice"] = has_unit_price
    if price_in_cents is not None:
        body["priceInCents"] = price_in_cents
    if unit is not None:
        body["unit"] = unit
    data = b.create_expense_category(ws, body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Category created: {d.get('name', '')} [{d.get('id', '')}]"
    ))


@expense_categories.command("update")
@click.argument("category_id")
@click.option("--name", default=None, help="New name")
@click.option("--has-unit-price/--no-unit-price", "has_unit_price", default=None,
              help="Whether category has a unit price")
@click.option("--price-in-cents", "price_in_cents", default=None, type=int,
              help="Price in cents")
@click.option("--unit", default=None, help="Unit label (e.g. 'mile', 'km')")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def expense_categories_update(ctx, category_id, name, has_unit_price, price_in_cents, unit, use_json):
    """Update an expense category."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {}
    if name is not None:
        body["name"] = name
    if has_unit_price is not None:
        body["hasUnitPrice"] = has_unit_price
    if price_in_cents is not None:
        body["priceInCents"] = price_in_cents
    if unit is not None:
        body["unit"] = unit
    result = b.update_expense_category(ws, category_id, body)
    _out(ctx, result, lambda _: repl_skin.success(f"Updated expense category {category_id}"))


@expense_categories.command("delete")
@click.argument("category_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def expense_categories_delete(ctx, category_id, confirm, use_json):
    """Delete an expense category."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"category {category_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_expense_category(ws, category_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Category {category_id} deleted."))


@expense_categories.command("archive")
@click.argument("category_id")
@click.option("--archived/--active", default=True, help="Archive or activate the category (default: archive)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def expense_categories_archive(ctx, category_id, archived, use_json):
    """Archive or activate an expense category."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.archive_expense_category(ws, category_id, {"archived": archived})
    _out(ctx, data, lambda _: repl_skin.success(
        f"Category {category_id} {'archived' if archived else 'activated'}."
    ))


# ── expenses extra commands ────────────────────────────────────────────

@expenses.command("receipt")
@click.argument("expense_id")
@click.argument("file_id")
@click.option("--output", default=None, help="Output file path (required without --base64)")
@click.option("--base64", "as_base64", is_flag=True, help="Output base64-encoded content as JSON")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def expenses_receipt(ctx, expense_id, file_id, output, as_base64, use_json):
    """Download an expense receipt file."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.download_expense_receipt(ws, expense_id, file_id)
    if as_base64:
        fmt.print_json({"content_base64": base64.b64encode(data).decode(), "bytes": len(data)})
    else:
        if not output:
            raise click.UsageError("--output is required when --base64 is not set")
        import os
        out_dir = os.path.dirname(output)
        if out_dir and not os.path.isdir(out_dir):
            raise click.UsageError(f"Output directory does not exist: {out_dir}")
        with open(output, "wb") as fh:
            fh.write(data)
        if ctx.obj.get("json"):
            fmt.print_json({"saved": output, "bytes": len(data)})
        else:
            repl_skin.success(f"Receipt saved to {output} ({len(data)} bytes).")
