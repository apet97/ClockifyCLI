from __future__ import annotations

from typing import Optional


class EntriesMixin:
    def list_entries(
        self,
        workspace_id: str,
        user_id: str,
        *,
        start: Optional[str] = None,
        end: Optional[str] = None,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        tags: Optional[list] = None,
        description: Optional[str] = None,
        in_progress: Optional[bool] = None,
        hydrated: Optional[bool] = None,
        get_week_before: Optional[str] = None,
        project_required: Optional[bool] = None,
        task_required: Optional[bool] = None,
        page_size: int = 50,
    ) -> list:
        """GET /v1/workspaces/{workspaceId}/user/{userId}/time-entries"""
        params: dict = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if project_id:
            params["project"] = project_id
        if task_id:
            params["task"] = task_id
        if description:
            params["description"] = description
        if in_progress is not None:
            params["in-progress"] = str(in_progress).lower()
        if tags:
            params["tags"] = ",".join(tags)
        if hydrated is not None:
            params["hydrated"] = str(hydrated).lower()
        if get_week_before:
            params["get-week-before"] = get_week_before
        if project_required is not None:
            params["project-required"] = str(project_required).lower()
        if task_required is not None:
            params["task-required"] = str(task_required).lower()
        return self._get_all_pages(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/user/{user_id}/time-entries",
            params=params,
            page_size=page_size,
            entity="time entry",
        )

    def get_entry(self, workspace_id: str, entry_id: str, *, hydrated: Optional[bool] = None) -> dict:
        """GET /v1/workspaces/{workspaceId}/time-entries/{id}"""
        params: dict = {}
        if hydrated is not None:
            params["hydrated"] = str(hydrated).lower()
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-entries/{entry_id}",
            params=params or None,
            entity=f"time entry {entry_id}",
        )

    def create_entry(self, workspace_id: str, user_id: str, data: dict, *, from_entry: Optional[str] = None) -> dict:
        """POST /v1/workspaces/{workspaceId}/user/{userId}/time-entries"""
        url = self._url(f"/workspaces/{workspace_id}/user/{user_id}/time-entries")  # type: ignore[attr-defined]
        params: dict = {}
        if from_entry:
            params["from-entry"] = from_entry
        return self._request("POST", url, json_data=data, params=params or None, entity="time entry")  # type: ignore[attr-defined]

    def create_time_entry_direct(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/time-entries"""
        return self._post(f"/workspaces/{workspace_id}/time-entries", data, entity="time entry")  # type: ignore[attr-defined]

    def update_entry(self, workspace_id: str, entry_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/time-entries/{id}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-entries/{entry_id}", data,
            entity=f"time entry {entry_id}",
        )

    def delete_entry(self, workspace_id: str, entry_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/time-entries/{id}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-entries/{entry_id}",
            entity=f"time entry {entry_id}",
        )

    def bulk_delete_entries(self, workspace_id: str, user_id: str, entry_ids: list) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/user/{userId}/time-entries?time-entry-ids=..."""
        ids_param = ",".join(entry_ids)
        return self._request(  # type: ignore[attr-defined]
            "DELETE",
            self._url(f"/workspaces/{workspace_id}/user/{user_id}/time-entries"),  # type: ignore[attr-defined]
            params={"time-entry-ids": ids_param},
            entity="time entries (bulk)",
        )

    def bulk_update_entries(self, workspace_id: str, user_id: str, data: list, *, hydrated: Optional[bool] = None) -> dict:
        """PUT /v1/workspaces/{workspaceId}/user/{userId}/time-entries"""
        params: Optional[dict] = None
        if hydrated is not None:
            params = {"hydrated": str(hydrated).lower()}
        url = self._url(f"/workspaces/{workspace_id}/user/{user_id}/time-entries")  # type: ignore[attr-defined]
        return self._request("PUT", url, json_data=data, params=params, entity="time entries (bulk update)")  # type: ignore[attr-defined]

    def duplicate_entry(self, workspace_id: str, user_id: str, entry_id: str) -> dict:
        """POST /v1/workspaces/{workspaceId}/user/{userId}/time-entries/{id}/duplicate"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/user/{user_id}/time-entries/{entry_id}/duplicate",
            entity=f"time entry {entry_id}",
        )

    def mark_entries_invoiced(self, workspace_id: str, entry_ids: list, invoiced: bool) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/time-entries/invoiced"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-entries/invoiced",
            data={"timeEntryIds": entry_ids, "invoiced": invoiced},
            entity="time entries (invoiced)",
        )
