from __future__ import annotations

from typing import Optional


class GroupsMixin:
    def list_groups(self, workspace_id: str, *, name: Optional[str] = None, project_id: Optional[str] = None, sort_column: Optional[str] = None, sort_order: Optional[str] = None, include_team_managers: Optional[bool] = None, page: Optional[int] = None, page_size: Optional[int] = None, **extra_params) -> list:
        """GET /v1/workspaces/{workspaceId}/user-groups"""
        params: dict = dict(extra_params)
        if name:
            params["name"] = name
        if project_id:
            params["projectId"] = project_id
        if sort_column:
            params["sort-column"] = sort_column
        if sort_order:
            params["sort-order"] = sort_order
        if include_team_managers is not None:
            params["includeTeamManagers"] = str(include_team_managers).lower()
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/user-groups",
            params=params or None,
            entity="user group",
        )
        return data if isinstance(data, list) else []

    def create_group(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/user-groups"""
        return self._post(f"/workspaces/{workspace_id}/user-groups", data, entity="user group")  # type: ignore[attr-defined]

    def update_group(self, workspace_id: str, group_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/user-groups/{groupId}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/user-groups/{group_id}",
            data,
            entity=f"group {group_id}",
        )

    def delete_group(self, workspace_id: str, group_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/user-groups/{groupId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/user-groups/{group_id}",
            entity=f"group {group_id}",
        )

    def add_users_to_group(self, workspace_id: str, group_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/user-groups/{groupId}/users"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/user-groups/{group_id}/users", data,
            entity="user group members",
        )

    def remove_user_from_group(self, workspace_id: str, group_id: str, user_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/user-groups/{groupId}/users/{userId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/user-groups/{group_id}/users/{user_id}",
            entity=f"user {user_id} from group {group_id}",
        )


class HolidaysMixin:
    def list_holidays(self, workspace_id: str, **params) -> list:
        """GET /v1/workspaces/{workspaceId}/holidays"""
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/holidays",
            params=params or None,
            entity="holiday",
        )
        return data if isinstance(data, list) else []

    def create_holiday(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/holidays"""
        return self._post(f"/workspaces/{workspace_id}/holidays", data, entity="holiday")  # type: ignore[attr-defined]

    def update_holiday(self, workspace_id: str, holiday_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/holidays/{holidayId}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/holidays/{holiday_id}",
            data,
            entity=f"holiday {holiday_id}",
        )

    def delete_holiday(self, workspace_id: str, holiday_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/holidays/{holidayId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/holidays/{holiday_id}",
            entity=f"holiday {holiday_id}",
        )

    def list_holidays_in_period(
        self,
        workspace_id: str,
        start: str,
        end: str,
        assigned_to: Optional[str] = None,
    ) -> list:
        """GET /v1/workspaces/{workspaceId}/holidays/in-period"""
        params: dict = {"start": start, "end": end}
        if assigned_to:
            params["assignedTo"] = assigned_to
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/holidays/in-period",
            params=params,
            entity="holiday",
        )
        return data if isinstance(data, list) else []


class CustomFieldsMixin:
    def list_custom_fields(self, workspace_id: str, *, name: Optional[str] = None, status: Optional[str] = None, entity_types: Optional[list] = None) -> list:
        """GET /v1/workspaces/{workspaceId}/custom-fields"""
        params: dict = {}
        if name:
            params["name"] = name
        if status:
            params["status"] = status
        if entity_types:
            params["entity-type"] = ",".join(entity_types)
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/custom-fields",
            params=params or None,
            entity="custom field",
        )
        return data if isinstance(data, list) else []

    def create_custom_field(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/custom-fields"""
        return self._post(f"/workspaces/{workspace_id}/custom-fields", data, entity="custom field")  # type: ignore[attr-defined]

    def update_custom_field(self, workspace_id: str, field_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/custom-fields/{fieldId}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/custom-fields/{field_id}",
            data,
            entity=f"custom field {field_id}",
        )

    def delete_custom_field(self, workspace_id: str, field_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/custom-fields/{fieldId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/custom-fields/{field_id}",
            entity=f"custom field {field_id}",
        )


class EntitiesMixin:
    def list_created_entities(
        self, workspace_id: str, entity_type: str, start: str, end: str,
        *, page: Optional[int] = None, page_size: Optional[int] = None,
    ) -> list:
        """GET /v1/workspaces/{workspaceId}/entities/created"""
        params: dict = {"entityType": entity_type, "start": start, "end": end}
        if page is not None:
            params["page"] = str(page)
        if page_size is not None:
            params["page-size"] = str(page_size)
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/entities/created",
            params=params,
            entity="created entity",
        )
        return data if isinstance(data, list) else []

    def list_deleted_entities(
        self, workspace_id: str, entity_type: str, start: str, end: str,
        *, page: Optional[int] = None, page_size: Optional[int] = None,
    ) -> list:
        """GET /v1/workspaces/{workspaceId}/entities/deleted"""
        params: dict = {"entityType": entity_type, "start": start, "end": end}
        if page is not None:
            params["page"] = str(page)
        if page_size is not None:
            params["page-size"] = str(page_size)
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/entities/deleted",
            params=params,
            entity="deleted entity",
        )
        return data if isinstance(data, list) else []

    def list_updated_entities(
        self, workspace_id: str, entity_type: str, start: str, end: str,
        *, page: Optional[int] = None, page_size: Optional[int] = None,
    ) -> list:
        """GET /v1/workspaces/{workspaceId}/entities/updated"""
        params: dict = {"entityType": entity_type, "start": start, "end": end}
        if page is not None:
            params["page"] = str(page)
        if page_size is not None:
            params["page-size"] = str(page_size)
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/entities/updated",
            params=params,
            entity="updated entity",
        )
        return data if isinstance(data, list) else []
