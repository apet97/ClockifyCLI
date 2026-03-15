from __future__ import annotations

from typing import Optional


class ApprovalsMixin:
    def list_approvals(self, workspace_id: str, *, status: Optional[str] = None, sort_column: Optional[str] = None, sort_order: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None, **extra_params) -> list:
        """GET /v1/workspaces/{workspaceId}/approval-requests"""
        params: dict = dict(extra_params)
        if status:
            params["status"] = status
        if sort_column:
            params["sort-column"] = sort_column
        if sort_order:
            params["sort-order"] = sort_order
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/approval-requests",
            params=params or None,
            entity="approval request",
        )
        return data if isinstance(data, list) else data.get("approvalRequests", []) if isinstance(data, dict) else []

    def submit_approval(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/approval-requests"""
        return self._post(f"/workspaces/{workspace_id}/approval-requests", data, entity="approval request")  # type: ignore[attr-defined]

    def submit_approval_for_user(self, workspace_id: str, user_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/approval-requests/users/{userId}"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/approval-requests/users/{user_id}", data,
            entity="approval request",
        )

    def update_approval(self, workspace_id: str, approval_id: str, data: dict) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/approval-requests/{approvalRequestId}"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/approval-requests/{approval_id}",
            data,
            entity=f"approval {approval_id}",
        )

    def resubmit_approval(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/approval-requests/resubmit-entries-for-approval"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/approval-requests/resubmit-entries-for-approval",
            data,
            entity="approval resubmission",
        )

    def resubmit_approval_for_user(self, workspace_id: str, user_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/approval-requests/users/{userId}/resubmit-entries-for-approval"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/approval-requests/users/{user_id}/resubmit-entries-for-approval",
            data,
            entity="approval resubmission",
        )
