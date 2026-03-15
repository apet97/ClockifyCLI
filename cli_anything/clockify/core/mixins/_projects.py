from __future__ import annotations

from typing import Optional


class ProjectsMixin:
    def list_projects(
        self,
        workspace_id: str,
        *,
        name: Optional[str] = None,
        archived: Optional[bool] = None,
        billable: Optional[bool] = None,
        client_ids: Optional[list] = None,
        strict_name_search: Optional[bool] = None,
        contains_client: Optional[bool] = None,
        client_status: Optional[str] = None,
        contains_user: Optional[bool] = None,
        user_status: Optional[str] = None,
        contains_group: Optional[bool] = None,
        user_groups: Optional[list] = None,
        is_template: Optional[bool] = None,
        hydrated: Optional[bool] = None,
        access: Optional[str] = None,
        sort_column: Optional[str] = None,
        sort_order: Optional[str] = None,
        users: Optional[list] = None,
        expense_limit: Optional[int] = None,
        expense_date: Optional[str] = None,
        page: Optional[int] = None,
        page_size: int = 50,
    ) -> list:
        """GET /v1/workspaces/{workspaceId}/projects"""
        params: dict = {}
        if name:
            params["name"] = name
        if archived is not None:
            params["archived"] = str(archived).lower()
        if billable is not None:
            params["billable"] = str(billable).lower()
        if client_ids:
            params["clients"] = ",".join(client_ids)
        if strict_name_search is not None:
            params["strict-name-search"] = str(strict_name_search).lower()
        if contains_client is not None:
            params["contains-client"] = str(contains_client).lower()
        if client_status:
            params["client-status"] = client_status
        if contains_user is not None:
            params["contains-user"] = str(contains_user).lower()
        if user_status:
            params["user-status"] = user_status
        if contains_group is not None:
            params["contains-group"] = str(contains_group).lower()
        if user_groups:
            params["userGroups"] = ",".join(user_groups)
        if is_template is not None:
            params["is-template"] = str(is_template).lower()
        if hydrated is not None:
            params["hydrated"] = str(hydrated).lower()
        if access:
            params["access"] = access
        if sort_column:
            params["sort-column"] = sort_column
        if sort_order:
            params["sort-order"] = sort_order
        if users:
            params["users"] = ",".join(users)
        if expense_limit is not None:
            params["expense-limit"] = str(expense_limit)
        if expense_date:
            params["expense-date"] = expense_date
        if page is not None:
            params["page"] = str(page)
        return self._get_all_pages(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects",
            params=params,
            page_size=page_size,
            entity="project",
        )

    def get_project(
        self,
        workspace_id: str,
        project_id: str,
        *,
        hydrated: Optional[bool] = None,
        custom_field_entity_type: Optional[str] = None,
        expense_limit: Optional[int] = None,
        expense_date: Optional[str] = None,
    ) -> dict:
        """GET /v1/workspaces/{workspaceId}/projects/{projectId}"""
        params: dict = {}
        if hydrated is not None:
            params["hydrated"] = str(hydrated).lower()
        if custom_field_entity_type:
            params["custom-field-entity-type"] = custom_field_entity_type
        if expense_limit is not None:
            params["expense-limit"] = str(expense_limit)
        if expense_date:
            params["expense-date"] = expense_date
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}",
            params=params or None,
            entity=f"project {project_id}",
        )

    def create_project(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/projects"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects", data,
            entity="project",
        )

    def update_project(self, workspace_id: str, project_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/projects/{projectId}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}", data,
            entity=f"project {project_id}",
        )

    def delete_project(self, workspace_id: str, project_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/projects/{projectId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}",
            entity=f"project {project_id}",
        )

    def update_project_estimate(self, workspace_id: str, project_id: str, data: dict) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/projects/{projectId}/estimate"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/estimate",
            data,
            entity=f"project {project_id}",
        )

    def update_project_memberships(self, workspace_id: str, project_id: str, data: dict) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/projects/{projectId}/memberships"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/memberships",
            data,
            entity=f"project {project_id}",
        )

    def update_project_template(self, workspace_id: str, project_id: str, data: dict) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/projects/{projectId}/template"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/template",
            data,
            entity=f"project {project_id}",
        )

    def assign_project_members(self, workspace_id: str, project_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/projects/{projectId}/memberships"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/memberships", data,
            entity=f"project {project_id} memberships",
        )

    def update_project_user_cost_rate(self, workspace_id: str, project_id: str, user_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/projects/{projectId}/users/{userId}/cost-rate"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/users/{user_id}/cost-rate",
            data,
            entity=f"project {project_id} user {user_id} cost rate",
        )

    def update_project_user_hourly_rate(self, workspace_id: str, project_id: str, user_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/projects/{projectId}/users/{userId}/hourly-rate"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/users/{user_id}/hourly-rate",
            data,
            entity=f"project {project_id} user {user_id} hourly rate",
        )

    def list_project_custom_fields(self, workspace_id: str, project_id: str, *, status: Optional[str] = None, entity_types: Optional[list] = None) -> list:
        """GET /v1/workspaces/{workspaceId}/projects/{projectId}/custom-fields"""
        params: dict = {}
        if status:
            params["status"] = status
        if entity_types:
            params["entity-type"] = ",".join(entity_types)
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/custom-fields",
            params=params or None,
            entity=f"project {project_id} custom fields",
        )
        return data if isinstance(data, list) else []

    def delete_project_custom_field(
        self, workspace_id: str, project_id: str, field_id: str
    ) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/projects/{projectId}/custom-fields/{fieldId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/custom-fields/{field_id}",
            entity=f"custom field {field_id} from project {project_id}",
        )

    def edit_project_custom_field(self, workspace_id: str, project_id: str, field_id: str, data: dict) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/projects/{projectId}/custom-fields/{customFieldId}"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/custom-fields/{field_id}",
            data,
            entity=f"custom field {field_id}",
        )
