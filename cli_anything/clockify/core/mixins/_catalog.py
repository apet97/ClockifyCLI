from __future__ import annotations

from typing import Optional


class ClientsMixin:
    def list_clients(self, workspace_id: str, *, name: Optional[str] = None, archived: Optional[bool] = None, sort_column: Optional[str] = None, sort_order: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> list:
        """GET /v1/workspaces/{workspaceId}/clients"""
        params: dict = {}
        if name:
            params["name"] = name
        if archived is not None:
            params["archived"] = str(archived).lower()
        if sort_column:
            params["sort-column"] = sort_column
        if sort_order:
            params["sort-order"] = sort_order
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        if page is not None:
            data = self._get(f"/workspaces/{workspace_id}/clients", params=params or None, entity="client")  # type: ignore[attr-defined]
            return data if isinstance(data, list) else []
        return self._get_all_pages(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/clients", params=params,
            page_size=page_size or 50, entity="client",
        )

    def create_client(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/clients"""
        return self._post(f"/workspaces/{workspace_id}/clients", data, entity="client")  # type: ignore[attr-defined]

    def update_client(self, workspace_id: str, client_id: str, data: dict, *, query_params: Optional[dict] = None) -> dict:
        """PUT /v1/workspaces/{workspaceId}/clients/{id}"""
        url = self._url(f"/workspaces/{workspace_id}/clients/{client_id}")  # type: ignore[attr-defined]
        return self._request("PUT", url, json_data=data, params=query_params, entity=f"client {client_id}")  # type: ignore[attr-defined]

    def delete_client(self, workspace_id: str, client_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/clients/{id}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/clients/{client_id}",
            entity=f"client {client_id}",
        )

    def get_client(self, workspace_id: str, client_id: str) -> dict:
        """GET /v1/workspaces/{workspaceId}/clients/{clientId}"""
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/clients/{client_id}",
            entity=f"client {client_id}",
        )


class TagsMixin:
    def list_tags(self, workspace_id: str, *, name: Optional[str] = None, archived: Optional[bool] = None, strict_name_search: Optional[bool] = None, excluded_ids: Optional[list] = None, sort_column: Optional[str] = None, sort_order: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> list:
        """GET /v1/workspaces/{workspaceId}/tags"""
        params: dict = {}
        if name:
            params["name"] = name
        if archived is not None:
            params["archived"] = str(archived).lower()
        if strict_name_search is not None:
            params["strict-name-search"] = str(strict_name_search).lower()
        if excluded_ids:
            params["excluded-ids"] = ",".join(excluded_ids)
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
                f"/workspaces/{workspace_id}/tags", params=params, entity="tag"
            )
        return self._get_all_pages(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/tags", params=params,
            page_size=page_size or 50, entity="tag",
        )

    def create_tag(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/tags"""
        return self._post(f"/workspaces/{workspace_id}/tags", data)  # type: ignore[attr-defined]

    def update_tag(self, workspace_id: str, tag_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/tags/{id}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/tags/{tag_id}", data,
            entity=f"tag {tag_id}",
        )

    def delete_tag(self, workspace_id: str, tag_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/tags/{id}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/tags/{tag_id}",
            entity=f"tag {tag_id}",
        )

    def get_tag(self, workspace_id: str, tag_id: str) -> dict:
        """GET /v1/workspaces/{workspaceId}/tags/{tagId}"""
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/tags/{tag_id}",
            entity=f"tag {tag_id}",
        )
