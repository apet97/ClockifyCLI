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


# ── invoices ──────────────────────────────────────────────────────────

@click.group()
def invoices():
    """Invoice management."""
    pass


@invoices.command("list")
@click.option("--status", "statuses", multiple=True,
              type=click.Choice(["UNSENT", "SENT", "PAID", "PARTIALLY_PAID", "VOID", "OVERDUE"]),
              help="Filter by status (repeatable)")
@click.option("--sort-column", default=None,
              type=click.Choice(["ID", "CLIENT", "DUE_ON", "ISSUE_DATE", "AMOUNT", "BALANCE"]),
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
def invoices_list(ctx, statuses, sort_column, sort_order, page, page_size, limit, use_json):
    """List invoices."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_invoices(
        ws,
        statuses=list(statuses) if statuses else None,
        sort_column=sort_column or None,
        sort_order=sort_order or None,
        page=page,
        page_size=page_size,
    )
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_invoices)


@invoices.command("get")
@click.argument("invoice_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoices_get(ctx, invoice_id, use_json):
    """Get an invoice by ID."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.get_invoice(ws, invoice_id)
    _out(ctx, data)


@invoices.command("delete")
@click.argument("invoice_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoices_delete(ctx, invoice_id, confirm, use_json):
    """Delete an invoice."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"invoice {invoice_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_invoice(ws, invoice_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Invoice {invoice_id} deleted."))


@invoices.command("status")
@click.argument("invoice_id")
@click.option("--status", required=True,
              type=click.Choice(["UNSENT", "SENT", "PAID", "PARTIALLY_PAID", "VOID", "OVERDUE"]))
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoices_status(ctx, invoice_id, status, use_json):
    """Change an invoice's status."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.change_invoice_status(ws, invoice_id, {"invoiceStatus": status})
    _out(ctx, data, lambda _: repl_skin.success(f"Invoice {invoice_id} status → {status}."))


@invoices.command("create")
@click.option("--client-id", default=None, help="Client ID (24-character Clockify object ID)")
@click.option("--name", default=None, help="Invoice name/number")
@click.option("--due-date", "due_date", default=None, help="Due date (YYYY-MM-DD)")
@click.option("--issue-date", "issue_date", default=None, help="Issue date (YYYY-MM-DD)")
@click.option("--currency", default=None, help="3-letter ISO currency code, e.g. USD, EUR, GBP")
@click.option("--language", default=None, help="Language code, e.g. en")
@click.option("--note", default=None, help="Invoice note")
@click.option("--po-number", "po_number", default=None, help="Purchase order number")
@click.option("--tax", default=None, type=float, help="Tax percentage")
@click.option("--discount", default=None, type=float, help="Discount percentage")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoices_create(ctx, client_id, name, due_date, issue_date, currency, language, note, po_number, tax, discount, use_json):
    """Create a new invoice."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {}
    if client_id:
        body["clientId"] = client_id
    if name:
        body["number"] = name
    if due_date:
        body["dueDate"] = parse_date_arg(due_date)
    if issue_date:
        body["issuedDate"] = parse_date_arg(issue_date)
    if currency:
        body["currency"] = currency
    if language:
        body["language"] = language
    if note:
        body["note"] = note
    if po_number:
        body["poNumber"] = po_number
    if tax is not None:
        body["tax"] = tax
    if discount is not None:
        body["discount"] = discount
    result = b.create_invoice(ws, body)
    _out(ctx, result, lambda d: repl_skin.success(
        f"Created invoice: {d.get('id', result)}"
    ))


@invoices.command("update")
@click.argument("invoice_id")
@click.option("--name", default=None, help="Invoice name/number")
@click.option("--due-date", "due_date", default=None, help="Due date (YYYY-MM-DD)")
@click.option("--issue-date", "issue_date", default=None, help="Issue date (YYYY-MM-DD)")
@click.option("--currency", default=None, help="3-letter ISO currency code, e.g. USD, EUR, GBP")
@click.option("--language", default=None, help="Language code, e.g. en")
@click.option("--note", default=None, help="Invoice note")
@click.option("--subject", default=None, help="Invoice subject line")
@click.option("--po-number", "po_number", default=None, help="Purchase order number")
@click.option("--tax", default=None, type=float, help="Tax percentage")
@click.option("--tax2", default=None, type=float, help="Second tax percentage")
@click.option("--discount", default=None, type=float, help="Discount percentage")
@click.option("--client-id", "client_id", default=None, help="Client ID")
@click.option("--company-id", "company_id", default=None, help="Company ID")
@click.option("--tax-type", "tax_type", default=None,
              type=click.Choice(["COMPOUND", "SIMPLE", "NONE"]),
              help="Tax calculation type")
@click.option("--visible-zero-fields", "visible_zero_fields", default=None,
              type=click.Choice(["TAX", "TAX_2", "DISCOUNT"]),
              help="Zero-value fields to display")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoices_update(ctx, invoice_id, name, due_date, issue_date, currency, language, note, subject, po_number, tax, tax2, discount, client_id, company_id, tax_type, visible_zero_fields, use_json):
    """Update an invoice."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {}
    if name:
        body["number"] = name
    if due_date:
        body["dueDate"] = parse_date_arg(due_date)
    if issue_date:
        body["issuedDate"] = parse_date_arg(issue_date)
    if currency:
        body["currency"] = currency
    if language:
        body["language"] = language
    if note:
        body["note"] = note
    if po_number:
        body["poNumber"] = po_number
    if tax is not None:
        body["taxPercent"] = tax
    if tax2 is not None:
        body["tax2Percent"] = tax2
    if discount is not None:
        body["discountPercent"] = discount
    if subject:
        body["subject"] = subject
    if client_id:
        body["clientId"] = client_id
    if company_id:
        body["companyId"] = company_id
    if tax_type:
        body["taxType"] = tax_type
    if visible_zero_fields:
        body["visibleZeroFields"] = visible_zero_fields
    result = b.update_invoice(ws, invoice_id, body)
    _out(ctx, result, lambda _: repl_skin.success(f"Updated invoice {invoice_id}"))


@invoices.command("duplicate")
@click.argument("invoice_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoices_duplicate(ctx, invoice_id, use_json):
    """Duplicate an invoice."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.duplicate_invoice(ws, invoice_id)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Invoice duplicated [{d.get('id', '')}]"
    ))


@invoices.group("payments")
def invoice_payments():
    """Invoice payment management."""
    pass


@invoice_payments.command("list")
@click.argument("invoice_id")
@click.option("--page", default=None, type=int, help="Page number (1-based)")
@click.option("--page-size", "page_size", default=None, type=int, help="Items per page")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoice_payments_list(ctx, invoice_id, page, page_size, limit, use_json):
    """List payments for an invoice."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_invoice_payments(ws, invoice_id, page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_invoice_payments)


@invoice_payments.command("add")
@click.argument("invoice_id")
@click.option("--amount", required=True, type=int, help="Payment amount (integer, min 1)")
@click.option("--date", required=True, help="Payment date (YYYY-MM-DD)")
@click.option("--note", default="", help="Payment note (max 1000 chars)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoice_payments_add(ctx, invoice_id, amount, date, note, use_json):
    """Add a payment to an invoice."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.add_invoice_payment(ws, invoice_id, {
        "amount": amount,
        "paymentDate": parse_date_arg(date) + "T00:00:00Z",
        "note": note,
    })
    _out(ctx, data, lambda d: repl_skin.success(
        f"Payment added [{d.get('id', '')}]"
    ))


@invoice_payments.command("delete")
@click.argument("invoice_id")
@click.argument("payment_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoice_payments_delete(ctx, invoice_id, payment_id, confirm, use_json):
    """Delete an invoice payment."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"payment {payment_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_invoice_payment(ws, invoice_id, payment_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Payment {payment_id} deleted."))


# ── invoices extra commands ────────────────────────────────────────────

@invoices.command("settings")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoices_settings(ctx, use_json):
    """Get invoice settings."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.get_invoice_settings(ws)
    _out(ctx, data)


@invoices.command("settings-update")
@click.option("--currency", default=None, help="Currency code")
@click.option("--tax1", type=float, default=None, help="Tax 1 percentage")
@click.option("--tax2", type=float, default=None, help="Tax 2 percentage")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoices_settings_update(ctx, currency, tax1, tax2, use_json):
    """Update invoice settings."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body = {k: v for k, v in {
        "currency": currency, "tax1": tax1, "tax2": tax2
    }.items() if v is not None}
    result = b.update_invoice_settings(ws, body)
    _out(ctx, result, lambda _: repl_skin.success("Invoice settings updated."))


@invoices.command("export")
@click.argument("invoice_id")
@click.option("--output", default=None, help="Output PDF file path (required without --base64)")
@click.option("--base64", "as_base64", is_flag=True, help="Output base64-encoded content as JSON")
@click.option("--user-locale", "user_locale", required=True, help="Locale for the export (e.g. en)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoices_export(ctx, invoice_id, output, as_base64, user_locale, use_json):
    """Export an invoice as a PDF file."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.export_invoice(ws, invoice_id, user_locale=user_locale)
    if as_base64:
        fmt.print_json({"content_base64": base64.b64encode(data).decode(), "bytes": len(data)})
    else:
        if not output:
            raise click.UsageError("--output is required when --base64 is not set")
        with open(output, "wb") as fh:
            fh.write(data)
        if ctx.obj.get("json"):
            fmt.print_json({"saved": output, "bytes": len(data)})
        else:
            repl_skin.success(f"Invoice exported to {output} ({len(data)} bytes).")


@invoices.command("filter")
@click.option("--status", "statuses", multiple=True,
              type=click.Choice(["UNSENT", "SENT", "PAID", "PARTIALLY_PAID", "VOID", "OVERDUE"]),
              help="Filter by status (repeatable)")
@click.option("--client", default=None, help="Filter by client ID")
@click.option("--company", default=None, help="Filter by company ID")
@click.option("--invoice-number", "invoice_number", default=None, help="Search by invoice number")
@click.option("--strict-search/--no-strict-search", default=None,
              help="Exact match for invoice number (default: partial match)")
@click.option("--issue-date-start", default=None, help="Issue date range start (YYYY-MM-DD)")
@click.option("--issue-date-end", default=None, help="Issue date range end (YYYY-MM-DD)")
@click.option("--exact-amount", "exact_amount", default=None, type=int, help="Filter by exact amount")
@click.option("--exact-balance", "exact_balance", default=None, type=int, help="Filter by exact balance")
@click.option("--greater-than-amount", "gt_amount", default=None, type=int, help="Amount greater than")
@click.option("--less-than-amount", "lt_amount", default=None, type=int, help="Amount less than")
@click.option("--greater-than-balance", "gt_balance", default=None, type=int, help="Balance greater than")
@click.option("--less-than-balance", "lt_balance", default=None, type=int, help="Balance less than")
@click.option("--sort-column", default=None,
              type=click.Choice(["ID", "CLIENT", "DUE_ON", "ISSUE_DATE", "AMOUNT", "BALANCE"]),
              help="Sort column")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--page", default=None, type=int, help="Page number (default 1)")
@click.option("--page-size", "page_size", default=None, type=int, help="Items per page (default 50)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def invoices_filter(ctx, statuses, client, company, invoice_number, strict_search, issue_date_start, issue_date_end, exact_amount, exact_balance, gt_amount, lt_amount, gt_balance, lt_balance, sort_column, sort_order, page, page_size, use_json):
    """Filter invoices with advanced criteria (POST /invoices/info)."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {}
    if statuses:
        body["statuses"] = list(statuses)
    if client:
        body["clients"] = {"ids": [client], "contains": "CONTAINS"}
    if company:
        body["companies"] = {"ids": [company]}
    if invoice_number:
        body["invoiceNumber"] = invoice_number
    if strict_search is not None:
        body["strictSearch"] = strict_search
    if issue_date_start or issue_date_end:
        issue_date: dict = {}
        if issue_date_start:
            issue_date["start"] = issue_date_start + "T00:00:00Z"
        if issue_date_end:
            issue_date["end"] = issue_date_end + "T23:59:59Z"
        body["issueDate"] = issue_date
    if exact_amount is not None:
        body["exactAmount"] = exact_amount
    if exact_balance is not None:
        body["exactBalance"] = exact_balance
    if gt_amount is not None:
        body["greaterThanAmount"] = gt_amount
    if lt_amount is not None:
        body["lessThanAmount"] = lt_amount
    if gt_balance is not None:
        body["greaterThanBalance"] = gt_balance
    if lt_balance is not None:
        body["lessThanBalance"] = lt_balance
    if sort_column:
        body["sortColumn"] = sort_column
    if sort_order:
        body["sortOrder"] = sort_order
    if page is not None:
        body["page"] = page
    if page_size is not None:
        body["pageSize"] = page_size
    data = b.filter_invoices(ws, body)
    _out(ctx, data, fmt.print_invoices)
