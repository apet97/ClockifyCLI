from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils import repl_skin
from cli_anything.clockify.utils.session import save_config_file
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, handle_errors,
)


@click.group()
def workspaces():
    """Workspace management."""
    pass


@workspaces.command("list")
@click.option("--role", "roles", multiple=True,
              type=click.Choice(["WORKSPACE_ADMIN", "OWNER", "TEAM_MANAGER", "PROJECT_MANAGER"]),
              help="Filter by role (repeatable)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def workspaces_list(ctx, roles, use_json):
    """List available workspaces."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    data = b.list_workspaces(roles=list(roles) if roles else None)
    _out(ctx, data, fmt.print_workspaces)


@workspaces.command("use")
@click.argument("workspace_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def workspaces_use(ctx, workspace_id, use_json):
    """Set the active workspace (saved to config file)."""
    if use_json:
        ctx.obj["json"] = True
    save_config_file({"workspace_id": workspace_id})
    session = ctx.obj["session"]
    if session:
        session.workspace_id = workspace_id
    result = {"workspace_id": workspace_id, "saved": True}
    _out(ctx, result, lambda _: repl_skin.success(
        f"Active workspace set to {workspace_id}"
    ))


@workspaces.command("create")
@click.argument("name")
@click.option("--organization-id", "organization_id", default=None, help="CAKE organization ID")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def workspaces_create(ctx, name, organization_id, use_json):
    """Create a new workspace."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    body: dict = {"name": name}
    if organization_id:
        body["organizationId"] = organization_id
    data = b.create_workspace(body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Workspace created: {d.get('name', '')} [{d.get('id', '')}]"
    ))


@workspaces.command("get")
@click.argument("workspace_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def workspaces_get(ctx, workspace_id, use_json):
    """Get a single workspace by ID."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    result = b.get_workspace(workspace_id)
    _out(ctx, result, lambda d: click.echo(f"Workspace: {d.get('name', d.get('id', workspace_id))}"))


@workspaces.command("invite")
@click.option("--email", required=True, help="Email of user to invite")
@click.option("--send-email/--no-email", default=True)
@click.option("--role", default=None,
              type=click.Choice(["WORKSPACE_ADMIN", "TEAM_MANAGER", "PROJECT_MANAGER"]),
              help="Role to assign to the invited user")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def workspaces_invite(ctx, email, send_email, role, use_json):
    """Invite a user to the workspace."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"email": email}
    if role:
        body["role"] = role
    data = b.add_user_to_workspace(ws, body, send_email=send_email)
    _out(ctx, data, lambda d: repl_skin.success(f"User invited: {email}"))


@workspaces.command("cost-rate")
@click.option("--amount", required=True, type=int, help="Rate amount in cents (integer)")
@click.option("--since", default=None, help="Effective since (ISO datetime, e.g. 2024-01-01T00:00:00Z)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def workspaces_cost_rate(ctx, amount, since, use_json):
    """Update workspace cost rate."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"amount": amount}
    if since:
        body["since"] = since
    data = b.update_workspace_cost_rate(ws, body)
    _out(ctx, data, lambda _: repl_skin.success("Workspace cost rate updated."))


@workspaces.command("hourly-rate")
@click.option("--amount", required=True, type=int, help="Rate amount in cents (integer)")
@click.option("--currency", default="USD", help="Currency code")
@click.option("--since", default=None, help="Effective since (ISO datetime, e.g. 2024-01-01T00:00:00Z)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def workspaces_hourly_rate(ctx, amount, currency, since, use_json):
    """Update workspace hourly rate."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"amount": amount, "currency": currency}
    if since:
        body["since"] = since
    data = b.update_workspace_hourly_rate(ws, body)
    _out(ctx, data, lambda _: repl_skin.success("Workspace hourly rate updated."))
