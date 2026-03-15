from __future__ import annotations

from typing import Optional


class TasksMixin:
    def list_tasks(self, workspace_id: str, project_id: str, *, name: Optional[str] = None, is_active: Optional[bool] = None, strict_name_search: Optional[bool] = None, sort_column: Optional[str] = None, sort_order: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> list:
        """GET /v1/workspaces/{workspaceId}/projects/{projectId}/tasks"""
        params: dict = {}
        if name:
            params["name"] = name
        if is_active is not None:
            params["is-active"] = str(is_active).lower()
        if strict_name_search is not None:
            params["strict-name-search"] = str(strict_name_search).lower()
        if sort_column:
            params["sort-column"] = sort_column
        if sort_order:
            params["sort-order"] = sort_order
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        if page is not None:
            return self._get(  # type: ignore[attr-defined]
                f"/workspaces/{workspace_id}/projects/{project_id}/tasks",
                params=params,
                entity="task",
            )
        return self._get_all_pages(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/tasks",
            params=params,
            page_size=page_size or 50,
            entity="task",
        )

    def get_task(self, workspace_id: str, project_id: str, task_id: str) -> dict:
        """GET /v1/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}"""
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}",
            entity=f"task {task_id}",
        )

    def create_task(
        self, workspace_id: str, project_id: str, data: dict,
        *, contains_assignee: Optional[bool] = None,
    ) -> dict:
        """POST /v1/workspaces/{workspaceId}/projects/{projectId}/tasks"""
        path = f"/workspaces/{workspace_id}/projects/{project_id}/tasks"
        if contains_assignee is not None:
            path += f"?contains-assignee={str(contains_assignee).lower()}"
        return self._post(path, data)  # type: ignore[attr-defined]

    def update_task(
        self,
        workspace_id: str,
        project_id: str,
        task_id: str,
        data: dict,
        *,
        contains_assignee: Optional[bool] = None,
        membership_status: Optional[str] = None,
    ) -> dict:
        """PUT /v1/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}"""
        params: dict = {}
        if contains_assignee is not None:
            params["contains-assignee"] = str(contains_assignee).lower()
        if membership_status:
            params["membership-status"] = membership_status
        url = self._url(f"/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}")  # type: ignore[attr-defined]
        return self._request("PUT", url, json_data=data, params=params or None, entity=f"task {task_id}")  # type: ignore[attr-defined]

    def delete_task(self, workspace_id: str, project_id: str, task_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}",
            entity=f"task {task_id}",
        )

    def update_task_cost_rate(
        self, workspace_id: str, project_id: str, task_id: str, data: dict
    ) -> dict:
        """PUT /v1/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/cost-rate"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/cost-rate",
            data,
            entity=f"task {task_id}",
        )

    def update_task_hourly_rate(
        self, workspace_id: str, project_id: str, task_id: str, data: dict
    ) -> dict:
        """PUT /v1/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/hourly-rate"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/hourly-rate",
            data,
            entity=f"task {task_id}",
        )
