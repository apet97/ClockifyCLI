from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils import repl_skin
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, handle_errors,
)

# ── webhooks ──────────────────────────────────────────────────────────

_WEBHOOK_EVENTS = [
    "NEW_PROJECT", "NEW_TASK", "NEW_CLIENT", "NEW_TIMER_STARTED", "TIMER_STOPPED",
    "TIME_ENTRY_UPDATED", "TIME_ENTRY_DELETED", "TIME_ENTRY_SPLIT", "NEW_TIME_ENTRY",
    "TIME_ENTRY_RESTORED", "NEW_TAG", "USER_DELETED_FROM_WORKSPACE",
    "USER_JOINED_WORKSPACE", "USER_DEACTIVATED_ON_WORKSPACE",
    "USER_ACTIVATED_ON_WORKSPACE", "USER_EMAIL_CHANGED", "USER_UPDATED",
    "NEW_INVOICE", "INVOICE_UPDATED", "NEW_APPROVAL_REQUEST",
    "APPROVAL_REQUEST_STATUS_UPDATED", "TIME_OFF_REQUESTED",
    "TIME_OFF_REQUEST_UPDATED", "TIME_OFF_REQUEST_APPROVED",
    "TIME_OFF_REQUEST_REJECTED", "TIME_OFF_REQUEST_WITHDRAWN", "BALANCE_UPDATED",
    "TAG_UPDATED", "TAG_DELETED", "TASK_UPDATED", "CLIENT_UPDATED", "TASK_DELETED",
    "CLIENT_DELETED", "EXPENSE_RESTORED", "ASSIGNMENT_CREATED", "ASSIGNMENT_DELETED",
    "ASSIGNMENT_PUBLISHED", "ASSIGNMENT_UPDATED", "EXPENSE_CREATED",
    "EXPENSE_DELETED", "EXPENSE_UPDATED", "PROJECT_UPDATED", "PROJECT_DELETED",
    "USER_GROUP_CREATED", "USER_GROUP_UPDATED", "USER_GROUP_DELETED",
    "USERS_INVITED_TO_WORKSPACE", "LIMITED_USERS_ADDED_TO_WORKSPACE",
    "COST_RATE_UPDATED", "BILLABLE_RATE_UPDATED",
]


@click.group()
def webhooks():
    """Webhook management."""
    pass


@webhooks.command("list")
@click.option("--type", "type_filter", default=None,
              type=click.Choice(["USER_CREATED", "SYSTEM", "ADDON"]),
              help="Filter by webhook type")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def webhooks_list(ctx, type_filter, limit, use_json):
    """List webhooks."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_webhooks(ws, type_filter=type_filter or None)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_webhooks)


@webhooks.command("get")
@click.argument("webhook_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def webhooks_get(ctx, webhook_id, use_json):
    """Get a webhook by ID."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.get_webhook(ws, webhook_id)
    _out(ctx, data)


_TRIGGER_SOURCE_TYPES = [
    "PROJECT_ID", "USER_ID", "TAG_ID", "TASK_ID", "WORKSPACE_ID",
    "ASSIGNMENT_ID", "EXPENSE_ID",
]

@webhooks.command("create")
@click.option("--url", required=True, help="Webhook target URL")
@click.option("--name", required=True, help="Webhook name")
@click.option("--event", "webhook_event", default="NEW_TIME_ENTRY",
              type=click.Choice(_WEBHOOK_EVENTS), help="Webhook event type")
@click.option("--trigger-source-type", "trigger_source_type", default=None,
              type=click.Choice(_TRIGGER_SOURCE_TYPES), help="Trigger source type (e.g. PROJECT_ID)")
@click.option("--trigger-source", "trigger_sources", multiple=True, help="Trigger source ID (repeatable)")
@click.option("--worker-url", "worker_url", default=None, help="Secondary delivery URL")
@click.option("--enabled/--disabled", default=True, help="Enable or disable the webhook (default: enabled)")
@click.option("--auth-header", "auth_header", default=None, help="Authorization header value sent on delivery")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def webhooks_create(ctx, url, name, webhook_event, trigger_source_type, trigger_sources, worker_url, enabled, auth_header, use_json):
    """Create a webhook."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"url": url, "name": name, "webhookEvent": webhook_event, "enabled": enabled}
    if trigger_source_type:
        body["triggerSourceType"] = trigger_source_type
    if trigger_sources:
        body["triggerSource"] = list(trigger_sources)
    if worker_url:
        body["workerUrl"] = worker_url
    if auth_header:
        body["authorizationHeader"] = auth_header
    data = b.create_webhook(ws, body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Webhook created: {d.get('name', '')} [{d.get('id', '')}]"
    ))


@webhooks.command("update")
@click.argument("webhook_id")
@click.option("--url", default=None)
@click.option("--name", default=None)
@click.option("--event", "webhook_event", default=None,
              type=click.Choice(_WEBHOOK_EVENTS), help="Webhook event type")
@click.option("--trigger-source-type", "trigger_source_type", default=None,
              type=click.Choice(_TRIGGER_SOURCE_TYPES), help="Trigger source type")
@click.option("--trigger-source", "trigger_sources", multiple=True, help="Trigger source ID (repeatable)")
@click.option("--enabled/--disabled", default=None, help="Enable or disable the webhook")
@click.option("--auth-header", "auth_header", default=None, help="Authorization header value sent on delivery")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def webhooks_update(ctx, webhook_id, url, name, webhook_event, trigger_source_type, trigger_sources, enabled, auth_header, use_json):
    """Update a webhook."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    existing = b.get_webhook(ws, webhook_id)
    body = dict(existing)
    if url:
        body["url"] = url
    if name:
        body["name"] = name
    if webhook_event:
        body["webhookEvent"] = webhook_event
    if trigger_source_type:
        body["triggerSourceType"] = trigger_source_type
    if trigger_sources:
        body["triggerSource"] = list(trigger_sources)
    if enabled is not None:
        body["enabled"] = enabled
    if auth_header:
        body["authorizationHeader"] = auth_header
    data = b.update_webhook(ws, webhook_id, body)
    _out(ctx, data, lambda _: repl_skin.success(f"Webhook {webhook_id} updated."))


@webhooks.command("delete")
@click.argument("webhook_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def webhooks_delete(ctx, webhook_id, confirm, use_json):
    """Delete a webhook."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"webhook {webhook_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_webhook(ws, webhook_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Webhook {webhook_id} deleted."))


@webhooks.command("logs")
@click.argument("webhook_id")
@click.option("--from", "from_date", default=None, help="Start datetime (ISO format)")
@click.option("--to", default=None, help="End datetime (ISO format)")
@click.option("--sort-by-newest/--sort-by-oldest", "sort_by_newest", default=None,
              help="Sort order for logs")
@click.option("--status", default=None,
              type=click.Choice(["ALL", "SUCCEEDED", "FAILED"]),
              help="Filter by delivery status")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def webhooks_logs(ctx, webhook_id, from_date, to, sort_by_newest, status, page, page_size, use_json):
    """Get webhook delivery logs."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {}
    if from_date:
        body["from"] = from_date
    if to:
        body["to"] = to
    if sort_by_newest is not None:
        body["sortByNewest"] = sort_by_newest
    if status:
        body["status"] = status
    data = b.get_webhook_logs(ws, webhook_id, data=body, page=page, page_size=page_size)
    _out(ctx, data)


# ── webhooks extra commands ────────────────────────────────────────────

@webhooks.command("addon-list")
@click.argument("addon_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def webhooks_addon_list(ctx, addon_id, use_json):
    """List webhooks for an add-on."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_addon_webhooks(ws, addon_id)
    _out(ctx, data)


@webhooks.command("regen-token")
@click.argument("webhook_id")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def webhooks_regen_token(ctx, webhook_id, use_json):
    """Regenerate a webhook's secret token."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.regenerate_webhook_token(ws, webhook_id)
    _out(ctx, data, lambda _: repl_skin.success(
        f"Webhook {webhook_id} token regenerated."))
