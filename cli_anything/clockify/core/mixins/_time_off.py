from __future__ import annotations

from typing import Optional


class TimeOffMixin:
    def list_time_off_policies(self, workspace_id: str, *, name: Optional[str] = None, status: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None, **extra_params) -> list:
        """GET /v1/workspaces/{workspaceId}/time-off/policies"""
        params: dict = dict(extra_params)
        if name:
            params["name"] = name
        if status:
            params["status"] = status
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/policies",
            params=params or None,
            entity="time off policy",
        )
        return data if isinstance(data, list) else []

    def create_time_off_policy(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/time-off/policies"""
        return self._post(f"/workspaces/{workspace_id}/time-off/policies", data, entity="time off policy")  # type: ignore[attr-defined]

    def get_time_off_policy(self, workspace_id: str, policy_id: str) -> dict:
        """GET /v1/workspaces/{workspaceId}/time-off/policies/{policyId}"""
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/policies/{policy_id}",
            entity=f"time off policy {policy_id}",
        )

    def update_time_off_policy(self, workspace_id: str, policy_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/time-off/policies/{policyId}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/policies/{policy_id}",
            data,
            entity=f"time off policy {policy_id}",
        )

    def delete_time_off_policy(self, workspace_id: str, policy_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/time-off/policies/{policyId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/policies/{policy_id}",
            entity=f"time off policy {policy_id}",
        )

    def create_time_off_request(self, workspace_id: str, policy_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/time-off/policies/{policyId}/requests"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/policies/{policy_id}/requests", data,
            entity="time off request",
        )

    def get_time_off_balance(self, workspace_id: str, user_id: str, *, sort: Optional[str] = None, sort_order: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> dict:
        """GET /v1/workspaces/{workspaceId}/time-off/balance/user/{userId}"""
        params: dict = {}
        if sort:
            params["sort"] = sort
        if sort_order:
            params["sort-order"] = sort_order
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/balance/user/{user_id}",
            params=params or None,
            entity=f"time off balance for user {user_id}",
        )

    def delete_time_off_request(self, workspace_id: str, policy_id: str, request_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/time-off/policies/{policyId}/requests/{requestId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/policies/{policy_id}/requests/{request_id}",
            entity=f"time off request {request_id}",
        )

    def update_time_off_request_status(self, workspace_id: str, policy_id: str, request_id: str, data: dict) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/time-off/policies/{policyId}/requests/{requestId}"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/policies/{policy_id}/requests/{request_id}",
            data,
            entity=f"time off request {request_id}",
        )

    def create_time_off_request_for_user(self, workspace_id: str, policy_id: str, user_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/time-off/policies/{policyId}/users/{userId}/requests"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/policies/{policy_id}/users/{user_id}/requests",
            data,
            entity="time off request",
        )

    def list_workspace_time_off_requests(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/time-off/requests"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/requests", data,
            entity="time off requests",
        )

    def get_policy_balance(self, workspace_id: str, policy_id: str, *, sort: Optional[str] = None, sort_order: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> dict:
        """GET /v1/workspaces/{workspaceId}/time-off/balance/policy/{policyId}"""
        params: dict = {}
        if sort:
            params["sort"] = sort
        if sort_order:
            params["sort-order"] = sort_order
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/balance/policy/{policy_id}",
            params=params or None,
            entity=f"time off policy balance {policy_id}",
        )

    def update_policy_balance(self, workspace_id: str, policy_id: str, data: dict) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/time-off/balance/policy/{policyId}"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/balance/policy/{policy_id}",
            data,
            entity=f"time off policy balance {policy_id}",
        )

    def update_time_off_policy_status(self, workspace_id: str, policy_id: str, data: dict) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/time-off/policies/{policyId}"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/time-off/policies/{policy_id}",
            data,
            entity=f"time off policy {policy_id}",
        )
