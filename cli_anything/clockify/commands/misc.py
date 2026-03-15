from __future__ import annotations

import click

from cli_anything.clockify.utils import formatters as fmt
from cli_anything.clockify.utils import repl_skin
from cli_anything.clockify.utils.time_utils import (
    parse_date_arg,
)
from cli_anything.clockify.utils.session import save_config_file
from ._helpers import (
    _ws, _user, _make_backend, _out,
    _resolve_project_id, _confirm_destructive, handle_errors,
    _parse_json_option,
)


# ── groups ────────────────────────────────────────────────────────────

@click.group()
def groups():
    """User group management."""
    pass


@groups.command("list")
@click.option("--name", default=None, help="Filter by group name")
@click.option("--project-id", default=None, help="Filter by project ID")
@click.option("--sort-column", default=None,
              type=click.Choice(["ID", "NAME"]),
              help="Sort column")
@click.option("--sort-order", default=None,
              type=click.Choice(["ASCENDING", "DESCENDING"]),
              help="Sort order")
@click.option("--include-team-managers", is_flag=True, default=False, help="Include team managers in response")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def groups_list(ctx, name, project_id, sort_column, sort_order, include_team_managers, page, page_size, limit, use_json):
    """List user groups."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_groups(ws, name=name or None, project_id=project_id or None, sort_column=sort_column or None, sort_order=sort_order or None, include_team_managers=True if include_team_managers else None, page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_groups)


@groups.command("create")
@click.argument("name")
@click.option("--user-id", "user_ids", multiple=True, help="Initial member user ID (repeatable)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def groups_create(ctx, name, user_ids, use_json):
    """Create a user group."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"name": name}
    if user_ids:
        body["userIds"] = list(user_ids)
    data = b.create_group(ws, body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Group created: {d.get('name', '')} [{d.get('id', '')}]"
    ))


@groups.command("update")
@click.argument("group_id")
@click.option("--name", default=None, help="New group name")
@click.option("--user-id", "user_ids", multiple=True, help="Member user ID (repeatable, replaces entire member list)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def groups_update(ctx, group_id, name, user_ids, use_json):
    """Update a user group."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {}
    if name is not None:
        body["name"] = name
    if user_ids:
        body["userIds"] = list(user_ids)
    data = b.update_group(ws, group_id, body)
    _out(ctx, data, lambda _: repl_skin.success(f"Group {group_id} updated."))


@groups.command("delete")
@click.argument("group_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def groups_delete(ctx, group_id, confirm, use_json):
    """Delete a user group."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"group {group_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_group(ws, group_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Group {group_id} deleted."))


@groups.command("add-user")
@click.argument("group_id")
@click.option("--user-id", required=True, help="User ID to add")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def groups_add_user(ctx, group_id, user_id, use_json):
    """Add a user to a group."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.add_users_to_group(ws, group_id, {"userId": user_id})
    _out(ctx, data, lambda _: repl_skin.success(f"User {user_id} added to group {group_id}."))


@groups.command("remove-user")
@click.argument("group_id")
@click.option("--user-id", required=True)
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def groups_remove_user(ctx, group_id, user_id, confirm, use_json):
    """Remove a user from a group."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"user {user_id} from group {group_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.remove_user_from_group(ws, group_id, user_id)
    _out(ctx, data, lambda _: repl_skin.success(
        f"User {user_id} removed from group {group_id}."
    ))


# ── holidays ──────────────────────────────────────────────────────────

@click.group()
def holidays():
    """Holiday management."""
    pass


@holidays.command("list")
@click.option("--assigned-to", default=None, help="Filter by assigned user ID")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def holidays_list(ctx, assigned_to, limit, use_json):
    """List holidays."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    params = {}
    if assigned_to:
        params["assigned-to"] = assigned_to
    data = b.list_holidays(ws, **params)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_holidays)


@holidays.command("in-period")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD)")
@click.option("--assigned-to", required=True, help="Filter by user ID")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def holidays_in_period(ctx, start, end, assigned_to, limit, use_json):
    """List holidays in a date range."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_holidays_in_period(
        ws,
        parse_date_arg(start),
        parse_date_arg(end),
        assigned_to=assigned_to,
    )
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_holidays)


@holidays.command("create")
@click.argument("name")
@click.option("--date", required=True, help="Holiday date (YYYY-MM-DD)")
@click.option("--recurring", "occurs_annually", is_flag=True, default=False, help="Holiday occurs annually")
@click.option("--color", default=None, help="Color hex code (e.g. #8BC34A)")
@click.option("--everyone/--not-everyone", "everyone_including_new", default=None, help="Apply to all users including new")
@click.option("--auto-time-entry/--no-auto-time-entry", "auto_time_entry", default=None, help="Create automatic time entries")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def holidays_create(ctx, name, date, occurs_annually, color, everyone_including_new, auto_time_entry, use_json):
    """Create a holiday."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {
        "name": name,
        "datePeriod": {"startDate": parse_date_arg(date) + "T00:00:00Z", "endDate": parse_date_arg(date) + "T23:59:59Z"},
        "occursAnnually": occurs_annually,
    }
    if color:
        body["color"] = color
    if everyone_including_new is not None:
        body["everyoneIncludingNew"] = everyone_including_new
    if auto_time_entry is not None:
        body["automaticTimeEntryCreation"] = {"enabled": auto_time_entry}
    data = b.create_holiday(ws, body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Holiday created: {d.get('name', '')} [{d.get('id', '')}]"
    ))


@holidays.command("update")
@click.argument("holiday_id")
@click.option("--name", default=None, help="New name")
@click.option("--date", default=None, help="Holiday date (YYYY-MM-DD)")
@click.option("--recurring/--no-recurring", "occurs_annually", default=None, help="Holiday occurs annually")
@click.option("--color", default=None, help="Color hex code (e.g. #8BC34A)")
@click.option("--everyone/--not-everyone", "everyone_including_new", default=None, help="Apply to all users including new")
@click.option("--auto-time-entry/--no-auto-time-entry", "auto_time_entry", default=None, help="Create automatic time entries")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def holidays_update(ctx, holiday_id, name, date, occurs_annually, color, everyone_including_new, auto_time_entry, use_json):
    """Update a holiday."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data: dict = {}
    if name is not None:
        data["name"] = name
    if date is not None:
        data["datePeriod"] = {"startDate": parse_date_arg(date) + "T00:00:00Z", "endDate": parse_date_arg(date) + "T23:59:59Z"}
    if occurs_annually is not None:
        data["occursAnnually"] = occurs_annually
    if color is not None:
        data["color"] = color
    if everyone_including_new is not None:
        data["everyoneIncludingNew"] = everyone_including_new
    if auto_time_entry is not None:
        data["automaticTimeEntryCreation"] = {"enabled": auto_time_entry}
    result = b.update_holiday(ws, holiday_id, data)
    _out(ctx, result, lambda _: repl_skin.success(f"Updated holiday {holiday_id}"))


@holidays.command("delete")
@click.argument("holiday_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def holidays_delete(ctx, holiday_id, confirm, use_json):
    """Delete a holiday."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"holiday {holiday_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_holiday(ws, holiday_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Holiday {holiday_id} deleted."))


# ── custom-fields ─────────────────────────────────────────────────────

@click.group("custom-fields")
def custom_fields():
    """Custom field management."""
    pass


@custom_fields.command("list")
@click.option("--name", default=None, help="Filter by name")
@click.option("--status", default=None,
              type=click.Choice(["INACTIVE", "VISIBLE", "INVISIBLE"]),
              help="Filter by status")
@click.option("--entity-type", "entity_types", multiple=True,
              type=click.Choice(["TIMEENTRY", "USER"]),
              help="Filter by entity type (repeatable)")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def custom_fields_list(ctx, name, status, entity_types, limit, use_json):
    """List custom fields."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_custom_fields(ws, name=name or None, status=status or None, entity_types=list(entity_types) if entity_types else None)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_custom_fields)


@custom_fields.command("create")
@click.argument("name")
@click.option("--type", "field_type", default="TXT",
              type=click.Choice(["TXT", "NUMBER", "DROPDOWN_SINGLE", "DROPDOWN_MULTIPLE",
                                 "CHECKBOX", "LINK"]))
@click.option("--description", default=None, help="Field description (max 3000 chars)")
@click.option("--entity-type", "entity_type", default=None,
              type=click.Choice(["TIMEENTRY", "USER"]),
              help="Entity type this field applies to")
@click.option("--status", default=None,
              type=click.Choice(["INACTIVE", "VISIBLE", "INVISIBLE"]),
              help="Field visibility status")
@click.option("--admin-only", "only_admin_can_edit", is_flag=True, default=False, help="Only admins can edit")
@click.option("--placeholder", default=None, help="Placeholder text")
@click.option("--allowed-value", "allowed_values", multiple=True, help="Allowed value for dropdowns (repeatable)")
@click.option("--default-value", "default_value", default=None, help="Default value (JSON string for complex types)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def custom_fields_create(ctx, name, field_type, description, entity_type, status, only_admin_can_edit, placeholder, allowed_values, default_value, use_json):
    """Create a custom field."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {"name": name, "type": field_type}
    if description:
        body["description"] = description
    if entity_type:
        body["entityType"] = entity_type
    if status:
        body["status"] = status
    if only_admin_can_edit:
        body["onlyAdminCanEdit"] = True
    if placeholder:
        body["placeholder"] = placeholder
    if allowed_values:
        body["allowedValues"] = list(allowed_values)
    if default_value:
        body["workspaceDefaultValue"] = _parse_json_option(default_value, "--default-value")
    data = b.create_custom_field(ws, body)
    _out(ctx, data, lambda d: repl_skin.success(
        f"Custom field created: {d.get('name', '')} [{d.get('id', '')}]"
    ))


@custom_fields.command("update")
@click.argument("field_id")
@click.option("--name", default=None, help="New name")
@click.option("--field-type", "field_type", default=None,
              type=click.Choice(["TXT", "NUMBER", "DROPDOWN_SINGLE", "DROPDOWN_MULTIPLE",
                                 "CHECKBOX", "LINK"]),
              help="Custom field type")
@click.option("--description", default=None, help="Field description (max 3000 chars)")
@click.option("--status", default=None,
              type=click.Choice(["INACTIVE", "VISIBLE", "INVISIBLE"]),
              help="Field visibility status")
@click.option("--admin-only/--anyone-can-edit", "only_admin_can_edit", default=None, help="Only admins can edit")
@click.option("--placeholder", default=None, help="Placeholder text")
@click.option("--required/--not-required", default=None, help="Make field required")
@click.option("--allowed-value", "allowed_values", multiple=True, help="Allowed value for dropdowns (repeatable, replaces existing)")
@click.option("--default-value", "default_value", default=None, help="Default value (JSON string for complex types)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def custom_fields_update(ctx, field_id, name, field_type, description, status, only_admin_can_edit, placeholder, required, allowed_values, default_value, use_json):
    """Update a custom field."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data: dict = {}
    if name is not None:
        data["name"] = name
    if field_type is not None:
        data["type"] = field_type
    if description is not None:
        data["description"] = description
    if status is not None:
        data["status"] = status
    if only_admin_can_edit is not None:
        data["onlyAdminCanEdit"] = only_admin_can_edit
    if placeholder is not None:
        data["placeholder"] = placeholder
    if required is not None:
        data["required"] = required
    if allowed_values:
        data["allowedValues"] = list(allowed_values)
    if default_value is not None:
        data["workspaceDefaultValue"] = _parse_json_option(default_value, "--default-value")
    result = b.update_custom_field(ws, field_id, data)
    _out(ctx, result, lambda _: repl_skin.success(f"Updated custom field {field_id}"))


@custom_fields.command("delete")
@click.argument("field_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def custom_fields_delete(ctx, field_id, confirm, use_json):
    """Delete a custom field."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"custom field {field_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_custom_field(ws, field_id)
    _out(ctx, data, lambda _: repl_skin.success(f"Custom field {field_id} deleted."))


@custom_fields.group("project")
def custom_fields_project():
    """Project-level custom field management."""
    pass


@custom_fields_project.command("list")
@click.argument("project_id")
@click.option("--status", default=None,
              type=click.Choice(["INACTIVE", "VISIBLE", "INVISIBLE"]),
              help="Filter by custom field status")
@click.option("--entity-type", "entity_types", multiple=True,
              help="Filter by entity type (repeatable)")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def custom_fields_project_list(ctx, project_id, status, entity_types, limit, use_json):
    """List custom fields for a project."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.list_project_custom_fields(ws, project_id, status=status,
                                        entity_types=list(entity_types) or None)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_custom_fields)


@custom_fields_project.command("delete")
@click.argument("project_id")
@click.argument("field_id")
@click.option("--confirm", is_flag=True)
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def custom_fields_project_delete(ctx, project_id, field_id, confirm, use_json):
    """Remove a custom field from a project."""
    if use_json:
        ctx.obj["json"] = True
    _confirm_destructive(ctx, f"custom field {field_id} from project {project_id}", confirm)
    b = _make_backend(ctx)
    ws = _ws(ctx)
    data = b.delete_project_custom_field(ws, project_id, field_id)
    _out(ctx, data, lambda _: repl_skin.success(
        f"Custom field {field_id} removed from project {project_id}."
    ))


@custom_fields_project.command("edit")
@click.argument("project_id")
@click.argument("field_id")
@click.option("--value", default=None, help="New default field value")
@click.option("--status", default=None,
              type=click.Choice(["INACTIVE", "VISIBLE", "INVISIBLE"]),
              help="Custom field status on this project")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def custom_fields_project_edit(ctx, project_id, field_id, value, status, use_json):
    """Edit a project custom field's default value and status."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    body: dict = {}
    if value is not None:
        body["defaultValue"] = value
    if status is not None:
        body["status"] = status
    data = b.edit_project_custom_field(ws, project_id, field_id, body)
    _out(ctx, data, lambda _: repl_skin.success(
        f"Custom field {field_id} updated for project {project_id}."
    ))


# ── entities ──────────────────────────────────────────────────────────

@click.group()
def entities():
    """Entity change tracking (experimental)."""
    pass


_ENTITY_DOC_TYPES = [
    "TIME_ENTRY", "TIME_ENTRY_CUSTOM_FIELD_VALUE", "TIME_ENTRY_RATE",
]


@entities.command("created")
@click.option("--type", "entity_type", required=True,
              type=click.Choice(_ENTITY_DOC_TYPES),
              help="Entity document type")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD)")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entities_created(ctx, entity_type, start, end, limit, page, page_size, use_json):
    """List created entities in a date range."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    start_iso = parse_date_arg(start) + "T00:00:00Z"
    end_iso = parse_date_arg(end) + "T23:59:59Z"
    data = b.list_created_entities(ws, entity_type, start_iso, end_iso, page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_entity_changes)


@entities.command("deleted")
@click.option("--type", "entity_type", required=True,
              type=click.Choice(_ENTITY_DOC_TYPES),
              help="Entity document type")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD)")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entities_deleted(ctx, entity_type, start, end, limit, page, page_size, use_json):
    """List deleted entities in a date range."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    start_iso = parse_date_arg(start) + "T00:00:00Z"
    end_iso = parse_date_arg(end) + "T23:59:59Z"
    data = b.list_deleted_entities(ws, entity_type, start_iso, end_iso, page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_entity_changes)


@entities.command("updated")
@click.option("--type", "entity_type", required=True,
              type=click.Choice(_ENTITY_DOC_TYPES),
              help="Entity document type")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD)")
@click.option("--limit", default=0, type=int, help="Max results (0=all)")
@click.option("--page", default=None, type=int, help="Page number")
@click.option("--page-size", "page_size", default=None, type=int, help="Page size")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def entities_updated(ctx, entity_type, start, end, limit, page, page_size, use_json):
    """List updated entities in a date range."""
    if use_json:
        ctx.obj["json"] = True
    b = _make_backend(ctx)
    ws = _ws(ctx)
    start_iso = parse_date_arg(start) + "T00:00:00Z"
    end_iso = parse_date_arg(end) + "T23:59:59Z"
    data = b.list_updated_entities(ws, entity_type, start_iso, end_iso, page=page, page_size=page_size)
    if limit > 0:
        data = data[:limit]
    _out(ctx, data, fmt.print_entity_changes)


# ── config ─────────────────────────────────────────────────────────────

@click.group()
def config():
    """Configuration management."""
    pass


@config.command("set-profile")
@click.argument("name")
@click.option("--api-key", default=None, help="API key for this profile")
@click.option("--workspace", default=None, help="Default workspace ID for this profile")
@click.option("--base-url", default=None, help="Base URL override")
@click.option("--reports-url", default=None, help="Reports URL override")
@click.option("--json", "use_json", is_flag=True)
@click.pass_context
@handle_errors
def config_set_profile(ctx, name, api_key, workspace, base_url, reports_url, use_json):
    """Create or update a named configuration profile."""
    if use_json:
        ctx.obj["json"] = True
    data: dict = {}
    if api_key:
        data["api_key"] = api_key
    if workspace:
        data["workspace_id"] = workspace
    if base_url:
        data["base_url"] = base_url
    if reports_url:
        data["reports_url"] = reports_url
    save_config_file(data, profile=name)
    _out(ctx, {"profile": name, "saved": True},
         lambda _: repl_skin.success(f"Profile '{name}' saved."))
