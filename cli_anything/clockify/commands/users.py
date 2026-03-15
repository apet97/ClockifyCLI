from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils import repl_skin
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, handle_errors,
)


# ── users ─────────────────────────────────────────────────────────────

@click.group()
def users():
    """User management."""
    pass


@users.command("list")
@click.option("--name", default=None, help="Filter by name")
@click.option("--email", default=None, help="Filter by email")
@click.option("--project-id", default=None, help="Filter users assigned to this project")
@click.option("--status", default=None,
              type=click.Choice(["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"]),
              help="Filter by membership status")
@click.option("--memberships", default=None,
              type=click.Choice(["ALL", "NONE", "WORKSPACE", "PROJECT", "USERGROUP"]),
              help="Filter by membership type")
@click.option("--include-roles", is_flag=True, default=False, help="Include role info in response")
@click.option("--account-statuses", default=None, help="Filter by account status")
@click.option("--sort-column", default=None,
              type=click.Choice(["ID", "EMAIL", "NAME", "NAME_LOWERCASE", "ACCESS", "HOURLYRATE", "COSTRATE"]),
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
def users_list(ctx, name, email, project_id, status, memberships, include_roles, account_statuses, sort_column, sort_order, page, page_size, limit, use_json):
    """List workspace members."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_users(ws, name=name or None, email=email or None, project_id=project_id or None, status=status or None, memberships=memberships or None, include_roles=True if include_roles else None, account_statuses=account_statuses or None, sort_column=sort_column or None, sort_order=sort_order or None, page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_users)


@users.command("me")
@click.option("--include-memberships", is_flag=True, default=False,
              help="Include workspace/project memberships in response")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def users_me(ctx, include_memberships, use_json):
    """Show current user profile."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    data = b.get_current_user(
        include_memberships=True if include_memberships else None,
    )
    _out(ctx, data)


# ── users (additional commands) ───────────────────────────────────────

@users.command("profile")
@click.argument("user_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def users_profile(ctx, user_id, use_json):
    """Get a workspace member's profile."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.get_member_profile(ws, user_id)
    _out(ctx, data)


@users.command("update-status")
@click.argument("user_id")
@click.option("--status", required=True,
              type=click.Choice(["ACTIVE", "INACTIVE"]),
              help="Membership status")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def users_update_status(ctx, user_id, status, use_json):
    """Update a user's workspace status."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.update_user_status(ws, user_id, {"status": status})
    _out(ctx, data, lambda _: repl_skin.success(f"User {user_id} status set to {status}."))


@users.command("managers")
@click.argument("user_id")
@click.option("--sort-column", default=None,
              type=click.Choice(["ID", "EMAIL", "NAME", "NAME_LOWERCASE", "ACCESS", "HOURLYRATE", "COSTRATE"]),
              help="Sort column")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def users_managers(ctx, user_id, sort_column, sort_order, page, page_size, use_json):
    """List a user's managers."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.get_user_managers(ws, user_id, sort_column=sort_column or None,
                                sort_order=sort_order or None,
                                page=page, page_size=page_size)
    _out(ctx, data, fmt.print_users)


@users.command("filter")
@click.option("--name", default=None, help="Filter by name")
@click.option("--status", default=None,
              type=click.Choice(["PENDING", "ACTIVE", "DECLINED", "INACTIVE", "ALL"]),
              help="Filter by membership status")
@click.option("--role", default=None,
              type=click.Choice(["WORKSPACE_ADMIN", "OWNER", "TEAM_MANAGER",
                                 "PROJECT_MANAGER"]),
              help="Filter by role")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def users_filter(ctx, name, status, role, use_json):
    """Filter users with advanced criteria."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = {k: v for k, v in {"name": name, "status": status, "role": role}.items()
            if v is not None}
    result = b.filter_users(ws, data)
    if ctx.obj.get("json"):
        fmt.print_json(result)
    else:
        items = result if isinstance(result, list) else [result]
        for u in items:
            click.echo(f"  {u.get('id', '')[:8]}  {u.get('name', u.get('email', ''))}")


@users.command("update-profile")
@click.argument("user_id")
@click.option("--name", default=None, help="New name")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def users_update_profile(ctx, user_id, name, use_json):
    """Update a workspace member profile."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = {k: v for k, v in {"name": name}.items() if v is not None}
    result = b.update_member_profile(ws, user_id, data)
    _out(ctx, result, lambda _: repl_skin.success(f"Updated profile for user {user_id}"))


@users.command("make-manager")
@click.argument("user_id")
@click.option("--role", required=True,
              type=click.Choice(["WORKSPACE_ADMIN", "TEAM_MANAGER", "PROJECT_MANAGER"]),
              help="Role to assign")
@click.option("--entity-id", required=True, help="Entity ID to scope the role to")
@click.option("--source-type", default=None,
              type=click.Choice(["USER_GROUP"]),
              help="Source type (only USER_GROUP)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def users_make_manager(ctx, user_id, role, entity_id, source_type, use_json):
    """Grant a role to a user."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"role": role, "entityId": entity_id}
    if source_type:
        body["sourceType"] = source_type
    result = b.add_manager_role(ws, user_id, body)
    _out(ctx, result, lambda _: repl_skin.success(f"Granted {role} role to user {user_id}"))


@users.command("remove-manager")
@click.argument("user_id")
@click.option("--role", required=True,
              type=click.Choice(["WORKSPACE_ADMIN", "TEAM_MANAGER", "PROJECT_MANAGER"]),
              help="Role to remove")
@click.option("--entity-id", required=True, help="Entity ID scoping the role")
@click.option("--source-type", default=None,
              type=click.Choice(["USER_GROUP"]),
              help="Source type (only USER_GROUP)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def users_remove_manager(ctx, user_id, role, entity_id, source_type, use_json):
    """Remove a role from a user."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"role": role, "entityId": entity_id}
    if source_type:
        body["sourceType"] = source_type
    result = b.remove_manager_role(ws, user_id, body)
    _out(ctx, result, lambda _: repl_skin.success(f"Removed {role} role from user {user_id}"))


@users.command("set-field")
@click.argument("user_id")
@click.argument("field_id")
@click.option("--value", required=True, help="Field value")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def users_set_field(ctx, user_id, field_id, value, use_json):
    """Set a custom field value for a user."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    result = b.update_user_custom_field(ws, user_id, field_id, {"value": value})
    _out(ctx, result, lambda _: repl_skin.success(f"Set field {field_id} for user {user_id}"))


# ── users extra commands ───────────────────────────────────────────────

@users.command("cost-rate")
@click.argument("user_id")
@click.option("--amount", required=True, type=int, help="Rate amount in cents (integer)")
@click.option("--since", default=None, help="Effective date (ISO datetime, e.g. 2020-01-01T00:00:00Z)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def users_cost_rate(ctx, user_id, amount, since, use_json):
    """Update a user's cost rate."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"amount": amount}
    if since is not None:
        body["since"] = since
    data = b.update_user_cost_rate(ws, user_id, body)
    _out(ctx, data, lambda _: repl_skin.success(f"Cost rate updated for user {user_id}."))


@users.command("hourly-rate")
@click.argument("user_id")
@click.option("--amount", required=True, type=int, help="Rate amount in cents (integer)")
@click.option("--since", default=None, help="Effective date (ISO datetime, e.g. 2020-01-01T00:00:00Z)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def users_hourly_rate(ctx, user_id, amount, since, use_json):
    """Update a user's hourly rate."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"amount": amount}
    if since is not None:
        body["since"] = since
    data = b.update_user_hourly_rate(ws, user_id, body)
    _out(ctx, data, lambda _: repl_skin.success(f"Hourly rate updated for user {user_id}."))


@users.command("upload-photo")
@click.argument("file_path")
@click.option("--content-type", default="image/jpeg", help="Image MIME type")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def users_upload_photo(ctx, file_path, content_type, use_json):
    """Upload a user profile photo."""
    if use_json:
        ctx.obj["json"] = True
    import os
    if not os.path.isfile(file_path):
        raise click.UsageError(f"File not found: {file_path}")
    b = _make_backend(ctx)
    with open(file_path, "rb") as fh:
        file_data = fh.read()
    filename = os.path.basename(file_path)
    data = b.upload_user_photo(file_data, filename=filename, content_type=content_type)
    _out(ctx, data, lambda _: repl_skin.success("Photo uploaded."))
