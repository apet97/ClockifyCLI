from __future__ import annotations

from typing import Optional


class SchedulingMixin:
    def list_all_assignments(self, workspace_id: str, *, name: Optional[str] = None, sort_column: Optional[str] = None, sort_order: Optional[str] = None, **extra_params) -> dict:
        """GET /v1/workspaces/{workspaceId}/scheduling/assignments/all"""
        params: dict = {k: v for k, v in extra_params.items() if v is not None}
        if name:
            params["name"] = name
        if sort_column:
            params["sort-column"] = sort_column
        if sort_order:
            params["sort-order"] = sort_order
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/scheduling/assignments/all",
            params=params or None,
            entity="scheduling assignments",
        )

    def create_recurring_assignment(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/scheduling/assignments/recurring"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/scheduling/assignments/recurring", data,
            entity="recurring assignment",
        )

    def update_recurring_assignment(self, workspace_id: str, assignment_id: str, data: dict) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/scheduling/assignments/recurring/{assignmentId}"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/scheduling/assignments/recurring/{assignment_id}",
            data,
            entity=f"recurring assignment {assignment_id}",
        )

    def delete_recurring_assignment(self, workspace_id: str, assignment_id: str, *, series_update_option: Optional[str] = None) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/scheduling/assignments/recurring/{assignmentId}"""
        params: Optional[dict] = None
        if series_update_option:
            params = {"seriesUpdateOption": series_update_option}
        url = self._url(f"/workspaces/{workspace_id}/scheduling/assignments/recurring/{assignment_id}")  # type: ignore[attr-defined]
        return self._request("DELETE", url, params=params, entity=f"recurring assignment {assignment_id}")  # type: ignore[attr-defined]

    def update_recurring_series(self, workspace_id: str, assignment_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/scheduling/assignments/series/{assignmentId}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/scheduling/assignments/series/{assignment_id}",
            data,
            entity=f"recurring series {assignment_id}",
        )

    def copy_assignment(self, workspace_id: str, assignment_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/scheduling/assignments/{assignmentId}/copy"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/scheduling/assignments/{assignment_id}/copy", data,
            entity="assignment copy",
        )

    def publish_assignments(self, workspace_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/scheduling/assignments/publish"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/scheduling/assignments/publish", data,
            entity="assignment publish",
        )

    def get_project_assignment_totals(self, workspace_id: str, project_id: str, *, start: Optional[str] = None, end: Optional[str] = None) -> dict:
        """GET /v1/workspaces/{workspaceId}/scheduling/assignments/projects/totals/{projectId}"""
        params: dict = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/scheduling/assignments/projects/totals/{project_id}",
            params=params or None,
            entity=f"project assignment totals {project_id}",
        )

    def get_project_assignments_batch(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/scheduling/assignments/projects/totals"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/scheduling/assignments/projects/totals", data,
            entity="project assignments",
        )

    def get_user_capacity(self, workspace_id: str, user_id: str, *, start: Optional[str] = None, end: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> dict:
        """GET /v1/workspaces/{workspaceId}/scheduling/assignments/users/{userId}/totals"""
        params: dict = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/scheduling/assignments/users/{user_id}/totals",
            params=params or None,
            entity=f"user capacity {user_id}",
        )

    def get_users_capacity_filter(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/scheduling/assignments/user-filter/totals"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/scheduling/assignments/user-filter/totals", data,
            entity="user capacity",
        )
