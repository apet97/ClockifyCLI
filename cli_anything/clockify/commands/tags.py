from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils import repl_skin
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, handle_errors,
)


@click.group()
def tags():
    """Tag management."""
    pass


@tags.command("list")
@click.option("--name", default=None, help="Filter by tag name")
@click.option("--archived", is_flag=True, default=False, help="Include archived tags")
@click.option("--strict-name-search", is_flag=True, default=False, help="Exact name match")
@click.option("--excluded-id", "excluded_ids", multiple=True, help="Tag ID to exclude (repeatable)")
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
def tags_list(ctx, name, archived, strict_name_search, excluded_ids, sort_column, sort_order, page, page_size, limit, use_json):
    """List tags."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_tags(ws, name=name or None, archived=True if archived else None, strict_name_search=True if strict_name_search else None, excluded_ids=list(excluded_ids) if excluded_ids else None, sort_column=sort_column or None, sort_order=sort_order or None, page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_tags)


@tags.command("create")
@click.argument("name")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def tags_create(ctx, name, use_json):
    """Create a tag."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"name": name}
    data = b.create_tag(ws, body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Tag created: {d.get('name', '')} [{d.get('id', '')}]"
    ))


@tags.command("update")
@click.argument("tag_id")
@click.option("--name", default=None, help="New tag name")
@click.option("--archived/--active", default=None, help="Archive or unarchive the tag")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def tags_update(ctx, tag_id, name, archived, use_json):
    """Update a tag."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {}
    if name is not None:
        body["name"] = name
    if archived is not None:
        body["archived"] = archived
    data = b.update_tag(ws, tag_id, body)
    _out(ctx, data, lambda _: repl_skin.success(f"Tag {tag_id} updated."))


@tags.command("get")
@click.argument("tag_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def tags_get(ctx, tag_id, use_json):
    """Get a single tag by ID."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    result = b.get_tag(ws, tag_id)
    _out(ctx, result, lambda d: click.echo(f"Tag: {d.get('name', d.get('id', tag_id))}"))


@tags.command("delete")
@click.argument("tag_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def tags_delete(ctx, tag_id, confirm, use_json):
    """Delete a tag."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"tag {tag_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_tag(ws, tag_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Tag {tag_id} deleted."))
