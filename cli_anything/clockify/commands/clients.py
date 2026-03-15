from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils import repl_skin
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, handle_errors,
)


@click.group()
def clients():
    """Client management."""
    pass


@clients.command("list")
@click.option("--name", default=None, help="Filter by client name")
@click.option("--archived", is_flag=True, default=False, help="Include archived clients")
@click.option("--sort-column", default=None,
              type=click.Choice(["NAME"]),
              help="Sort column")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def clients_list(ctx, name, archived, sort_column, sort_order, page, page_size, limit, use_json):
    """List clients."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_clients(ws, name=name or None, archived=True if archived else None, sort_column=sort_column or None, sort_order=sort_order or None, page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_clients)


@clients.command("create")
@click.argument("name")
@click.option("--note", default=None, help="Client note")
@click.option("--address", default=None, help="Client address")
@click.option("--email", default=None, help="Client email")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def clients_create(ctx, name, note, address, email, use_json):
    """Create a client."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"name": name}
    if note is not None:
        body["note"] = note
    if address is not None:
        body["address"] = address
    if email is not None:
        body["email"] = email
    data = b.create_client(ws, body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Client created: {d.get('name', '')} [{d.get('id', '')}]"
    ))


@clients.command("update")
@click.argument("client_id")
@click.option("--name", default=None, help="New client name")
@click.option("--note", default=None, help="Client note")
@click.option("--address", default=None, help="Client address")
@click.option("--email", default=None, help="Client email")
@click.option("--currency", "currency_id", default=None, help="Currency ID")
@click.option("--cc-email", "cc_emails", multiple=True, help="CC email address (repeatable, max 3)")
@click.option("--archived/--active", default=None, help="Archive or activate the client")
@click.option("--archive-projects", is_flag=True, default=False, help="Also archive client's projects")
@click.option("--mark-tasks-done", is_flag=True, default=False, help="Mark tasks as done when archiving")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def clients_update(ctx, client_id, name, note, address, email, currency_id, cc_emails, archived, archive_projects, mark_tasks_done, use_json):
    """Update a client."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {}
    if name is not None:
        body["name"] = name
    if note is not None:
        body["note"] = note
    if address is not None:
        body["address"] = address
    if email is not None:
        body["email"] = email
    if currency_id is not None:
        body["currencyId"] = currency_id
    if cc_emails:
        body["ccEmails"] = list(cc_emails)
    if archived is not None:
        body["archived"] = archived
    query_params: dict = {}
    if archive_projects:
        query_params["archive-projects"] = "true"
    if mark_tasks_done:
        query_params["mark-tasks-as-done"] = "true"
    data = b.update_client(ws, client_id, body, query_params=query_params or None)
    _out(ctx, data, lambda _: repl_skin.success(f"Client {client_id} updated."))


@clients.command("get")
@click.argument("client_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def clients_get(ctx, client_id, use_json):
    """Get a single client by ID."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    result = b.get_client(ws, client_id)
    _out(ctx, result, lambda d: click.echo(f"Client: {d.get('name', d.get('id', client_id))}"))


@clients.command("delete")
@click.argument("client_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def clients_delete(ctx, client_id, confirm, use_json):
    """Delete a client."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"client {client_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_client(ws, client_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Client {client_id} deleted."))
