from __future__ import annotations

from typing import Optional

from ._base import ClockifyAPIError


class TimerMixin:
    def start_timer(
        self,
        workspace_id: str,
        user_id: str,
        description: str = "",
        project_id: Optional[str] = None,
        tag_ids: Optional[list] = None,
        task_id: Optional[str] = None,
        start: Optional[str] = None,
        billable: Optional[bool] = None,
        entry_type: Optional[str] = None,
        custom_fields: Optional[list] = None,
    ) -> dict:
        """Start a running timer: POST time entry with start but no end.

        POST /v1/workspaces/{workspaceId}/user/{userId}/time-entries
        """
        from cli_anything.clockify.utils.time_utils import now_iso
        body: dict = {
            "start": start or now_iso(),
            "description": description,
        }
        if project_id:
            body["projectId"] = project_id
        if tag_ids:
            body["tagIds"] = tag_ids
        if task_id:
            body["taskId"] = task_id
        if billable is not None:
            body["billable"] = billable
        if entry_type:
            body["type"] = entry_type
        if custom_fields:
            body["customFields"] = custom_fields
        return self.create_entry(workspace_id, user_id, body)  # type: ignore[attr-defined]

    def stop_timer(self, workspace_id: str, user_id: str) -> dict:
        """Stop the running timer.

        PATCH /v1/workspaces/{workspaceId}/user/{userId}/time-entries
        body: {"end": "<now>"}
        """
        from cli_anything.clockify.utils.time_utils import now_iso
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/user/{user_id}/time-entries",
            data={"end": now_iso()},
            entity="timer",
        )

    def get_running_timer(
        self, workspace_id: str, user_id: str,
        *, page: Optional[int] = None, page_size: Optional[int] = None,
    ) -> Optional[dict]:
        """Return the currently running timer entry, or None.

        GET /v1/workspaces/{workspaceId}/time-entries/status/in-progress
        """
        params: dict = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        try:
            data = self._get(  # type: ignore[attr-defined]
                f"/workspaces/{workspace_id}/time-entries/status/in-progress",
                params=params or None,
                entity="running timer",
            )
        except ClockifyAPIError as e:
            if e.status_code == 404:
                return None
            raise
        if isinstance(data, list):
            return data[0] if data else None
        if isinstance(data, dict) and data:
            return data
        return None
