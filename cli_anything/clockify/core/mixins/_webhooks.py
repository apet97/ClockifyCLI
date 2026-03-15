from __future__ import annotations

from typing import Optional


class WebhooksMixin:
    def list_webhooks(self, workspace_id: str, *, type_filter: Optional[str] = None) -> list:
        """GET /v1/workspaces/{workspaceId}/webhooks"""
        params: dict = {}
        if type_filter:
            params["type"] = type_filter
        data = self._get(f"/workspaces/{workspace_id}/webhooks", params=params or None, entity="webhook")  # type: ignore[attr-defined]
        return data if isinstance(data, list) else []

    def create_webhook(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/webhooks"""
        return self._post(f"/workspaces/{workspace_id}/webhooks", data, entity="webhook")  # type: ignore[attr-defined]

    def get_webhook(self, workspace_id: str, webhook_id: str) -> dict:
        """GET /v1/workspaces/{workspaceId}/webhooks/{webhookId}"""
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/webhooks/{webhook_id}",
            entity=f"webhook {webhook_id}",
        )

    def update_webhook(self, workspace_id: str, webhook_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/webhooks/{webhookId}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/webhooks/{webhook_id}",
            data,
            entity=f"webhook {webhook_id}",
        )

    def delete_webhook(self, workspace_id: str, webhook_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/webhooks/{webhookId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/webhooks/{webhook_id}",
            entity=f"webhook {webhook_id}",
        )

    def get_webhook_logs(self, workspace_id: str, webhook_id: str, data: Optional[dict] = None, *, page: Optional[int] = None, page_size: Optional[int] = None) -> dict:
        """POST /v1/workspaces/{workspaceId}/webhooks/{webhookId}/logs"""
        params: dict = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        return self._request(  # type: ignore[attr-defined]
            "POST",
            self._url(f"/workspaces/{workspace_id}/webhooks/{webhook_id}/logs"),  # type: ignore[attr-defined]
            params=params or None,
            json_data=data or {},
        )

    def list_addon_webhooks(self, workspace_id: str, addon_id: str) -> dict:
        """GET /v1/workspaces/{workspaceId}/addons/{addonId}/webhooks"""
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/addons/{addon_id}/webhooks",
            entity=f"addon {addon_id} webhooks",
        )

    def regenerate_webhook_token(self, workspace_id: str, webhook_id: str) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/webhooks/{webhookId}/token"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/webhooks/{webhook_id}/token",
            entity=f"webhook {webhook_id} token",
        )
