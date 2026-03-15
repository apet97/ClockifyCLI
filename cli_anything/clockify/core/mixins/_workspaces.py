from __future__ import annotations

from typing import Optional


class WorkspacesMixin:
    def list_workspaces(self, *, roles: Optional[list] = None) -> list:
        """GET /v1/workspaces"""
        params: dict = {}
        if roles:
            params["roles"] = ",".join(roles)
        data = self._get("/workspaces", params=params or None)  # type: ignore[attr-defined]
        return data if isinstance(data, list) else []

    def get_workspace(self, workspace_id: str) -> dict:
        """GET /v1/workspaces/{workspaceId}"""
        return self._get(f"/workspaces/{workspace_id}", entity=f"workspace {workspace_id}")  # type: ignore[attr-defined]

    def create_workspace(self, data: dict) -> dict:
        """POST /v1/workspaces"""
        return self._post("/workspaces", data, entity="workspace")  # type: ignore[attr-defined]

    def update_workspace_cost_rate(self, workspace_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/cost-rate"""
        return self._put(f"/workspaces/{workspace_id}/cost-rate", data, entity="workspace cost rate")  # type: ignore[attr-defined]

    def update_workspace_hourly_rate(self, workspace_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/hourly-rate"""
        return self._put(f"/workspaces/{workspace_id}/hourly-rate", data, entity="workspace hourly rate")  # type: ignore[attr-defined]
