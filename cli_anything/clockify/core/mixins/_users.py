from __future__ import annotations

from typing import Optional


class UsersMixin:
    def get_current_user(self, *, include_memberships: Optional[bool] = None) -> dict:
        """GET /v1/user"""
        params: dict = {}
        if include_memberships is not None:
            params["include-memberships"] = str(include_memberships).lower()
        return self._get("/user", params=params or None, entity="current user")  # type: ignore[attr-defined]

    def list_users(self, workspace_id: str, *, name: Optional[str] = None, email: Optional[str] = None, project_id: Optional[str] = None, status: Optional[str] = None, memberships: Optional[str] = None, include_roles: Optional[bool] = None, account_statuses: Optional[str] = None, sort_column: Optional[str] = None, sort_order: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> list:
        """GET /v1/workspaces/{workspaceId}/users"""
        params: dict = {}
        if name:
            params["name"] = name
        if email:
            params["email"] = email
        if project_id:
            params["project-id"] = project_id
        if status:
            params["status"] = status
        if memberships:
            params["memberships"] = memberships
        if include_roles is not None:
            params["include-roles"] = str(include_roles).lower()
        if account_statuses:
            params["account-statuses"] = account_statuses
        if sort_column:
            params["sort-column"] = sort_column
        if sort_order:
            params["sort-order"] = sort_order
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        if page is not None:
            data = self._get(f"/workspaces/{workspace_id}/users", params=params or None, entity="user")  # type: ignore[attr-defined]
            return data if isinstance(data, list) else []
        return self._get_all_pages(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/users", params=params,
            page_size=page_size or 50, entity="user",
        )

    def add_user_to_workspace(self, workspace_id: str, data: dict, send_email: bool = False) -> dict:
        """POST /v1/workspaces/{workspaceId}/users"""
        return self._request(  # type: ignore[attr-defined]
            "POST",
            self._url(f"/workspaces/{workspace_id}/users"),  # type: ignore[attr-defined]
            params={"send-email": str(send_email).lower()},
            json_data=data,
            entity="workspace user invitation",
        )

    def update_user_status(self, workspace_id: str, user_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/users/{userId}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/users/{user_id}",
            data,
            entity=f"user {user_id}",
        )

    def get_member_profile(self, workspace_id: str, user_id: str) -> dict:
        """GET /v1/workspaces/{workspaceId}/member-profile/{userId}"""
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/member-profile/{user_id}",
            entity=f"member profile {user_id}",
        )

    def update_member_profile(self, workspace_id: str, user_id: str, data: dict) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/member-profile/{userId}"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/member-profile/{user_id}",
            data,
            entity=f"member profile {user_id}",
        )

    def filter_users(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/users/info"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/users/info", data,
            entity="users filter",
        )

    def get_user_managers(
        self,
        workspace_id: str,
        user_id: str,
        *,
        sort_column: Optional[str] = None,
        sort_order: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> list:
        """GET /v1/workspaces/{workspaceId}/users/{userId}/managers"""
        params: dict = {}
        if sort_column:
            params["sort-column"] = sort_column
        if sort_order:
            params["sort-order"] = sort_order
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/users/{user_id}/managers",
            params=params or None,
            entity=f"user {user_id} managers",
        )
        return data if isinstance(data, list) else []

    def add_manager_role(self, workspace_id: str, user_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/users/{userId}/roles"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/users/{user_id}/roles", data,
            entity=f"user {user_id} role",
        )

    def remove_manager_role(self, workspace_id: str, user_id: str, data: dict) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/users/{userId}/roles"""
        return self._request(  # type: ignore[attr-defined]
            "DELETE",
            self._url(f"/workspaces/{workspace_id}/users/{user_id}/roles"),  # type: ignore[attr-defined]
            json_data=data,
            entity=f"user {user_id} role",
        )

    def update_user_custom_field(
        self, workspace_id: str, user_id: str, field_id: str, data: dict
    ) -> dict:
        """PUT /v1/workspaces/{workspaceId}/users/{userId}/custom-field/{fieldId}/value"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/users/{user_id}/custom-field/{field_id}/value",
            data,
            entity=f"custom field {field_id}",
        )

    def upload_user_photo(self, file_data: bytes, filename: str = "photo.jpg", content_type: str = "image/jpeg") -> dict:
        """POST /v1/file/image — multipart upload (no workspace, separate endpoint)."""
        url = self._url("/file/image")  # type: ignore[attr-defined]
        headers = {k: v for k, v in self._headers().items() if k != "Content-Type"}  # type: ignore[attr-defined]
        resp = self._retry_request(  # type: ignore[attr-defined]
            lambda: self._http.post(  # type: ignore[attr-defined]
                url, headers=headers,
                files={"file": (filename, file_data, content_type)},
                timeout=self.reports_timeout,  # type: ignore[attr-defined]
            )
        )
        return self._handle_response(resp, "user photo")  # type: ignore[attr-defined]

    def update_user_cost_rate(self, workspace_id: str, user_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/users/{userId}/cost-rate"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/users/{user_id}/cost-rate",
            data,
            entity=f"user {user_id} cost rate",
        )

    def update_user_hourly_rate(self, workspace_id: str, user_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/users/{userId}/hourly-rate"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/users/{user_id}/hourly-rate",
            data,
            entity=f"user {user_id} hourly rate",
        )
