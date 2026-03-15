from __future__ import annotations

from typing import Optional


class ExpensesMixin:
    def list_expenses(self, workspace_id: str, user_id: Optional[str] = None, *, page: Optional[int] = None, page_size: Optional[int] = None) -> list:
        """GET /v1/workspaces/{workspaceId}/expenses"""
        params: dict = {}
        if user_id:
            params["user-id"] = user_id
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        if page is not None:
            return self._get(  # type: ignore[attr-defined]
                f"/workspaces/{workspace_id}/expenses",
                params=params or None,
                entity="expense",
            )
        return self._get_all_pages(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/expenses",
            params=params or None,
            page_size=page_size or 50,
            entity="expense",
        )

    def create_expense(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/expenses"""
        return self._post(f"/workspaces/{workspace_id}/expenses", data)  # type: ignore[attr-defined]

    def get_expense(self, workspace_id: str, expense_id: str) -> dict:
        """GET /v1/workspaces/{workspaceId}/expenses/{expenseId}"""
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/expenses/{expense_id}",
            entity=f"expense {expense_id}",
        )

    def update_expense(self, workspace_id: str, expense_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/expenses/{expenseId}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/expenses/{expense_id}",
            data,
            entity=f"expense {expense_id}",
        )

    def delete_expense(self, workspace_id: str, expense_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/expenses/{expenseId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/expenses/{expense_id}",
            entity=f"expense {expense_id}",
        )

    def list_expense_categories(self, workspace_id: str, *, name: Optional[str] = None, archived: Optional[bool] = None, sort_column: Optional[str] = None, sort_order: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> list:
        """GET /v1/workspaces/{workspaceId}/expenses/categories"""
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
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/expenses/categories",
            params=params or None,
            entity="expense category",
        )
        return data if isinstance(data, list) else []

    def create_expense_category(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/expenses/categories"""
        return self._post(f"/workspaces/{workspace_id}/expenses/categories", data)  # type: ignore[attr-defined]

    def update_expense_category(self, workspace_id: str, category_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/expenses/categories/{categoryId}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/expenses/categories/{category_id}",
            data,
            entity=f"expense category {category_id}",
        )

    def delete_expense_category(self, workspace_id: str, category_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/expenses/categories/{categoryId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/expenses/categories/{category_id}",
            entity=f"expense category {category_id}",
        )

    def download_expense_receipt(self, workspace_id: str, expense_id: str, file_id: str) -> bytes:
        """GET /v1/workspaces/{workspaceId}/expenses/{expenseId}/files/{fileId} (binary)"""
        return self._request(  # type: ignore[attr-defined]
            "GET",
            self._url(f"/workspaces/{workspace_id}/expenses/{expense_id}/files/{file_id}"),  # type: ignore[attr-defined]
            entity=f"expense receipt {file_id}",
            raw=True,
        )

    def archive_expense_category(self, workspace_id: str, category_id: str, data: dict) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/expenses/categories/{categoryId}/status"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/expenses/categories/{category_id}/status",
            data,
            entity=f"expense category {category_id}",
        )
