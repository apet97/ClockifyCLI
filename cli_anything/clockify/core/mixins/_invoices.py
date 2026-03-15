from __future__ import annotations

from typing import Optional


class InvoicesMixin:
    def list_invoices(self, workspace_id: str, *, statuses: Optional[list] = None, sort_column: Optional[str] = None, sort_order: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None, **extra_params) -> list:
        """GET /v1/workspaces/{workspaceId}/invoices"""
        params: dict = dict(extra_params)
        if statuses:
            params["statuses"] = ",".join(statuses)
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
                f"/workspaces/{workspace_id}/invoices",
                params=params or None,
                entity="invoice",
            )
        return self._get_all_pages(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/invoices",
            params=params or None,
            page_size=page_size or 50,
            entity="invoice",
        )

    def create_invoice(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/invoices"""
        return self._post(f"/workspaces/{workspace_id}/invoices", data, entity="invoice")  # type: ignore[attr-defined]

    def get_invoice(self, workspace_id: str, invoice_id: str) -> dict:
        """GET /v1/workspaces/{workspaceId}/invoices/{invoiceId}"""
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/invoices/{invoice_id}",
            entity=f"invoice {invoice_id}",
        )

    def update_invoice(self, workspace_id: str, invoice_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/invoices/{invoiceId}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/invoices/{invoice_id}",
            data,
            entity=f"invoice {invoice_id}",
        )

    def delete_invoice(self, workspace_id: str, invoice_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/invoices/{invoiceId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/invoices/{invoice_id}",
            entity=f"invoice {invoice_id}",
        )

    def change_invoice_status(self, workspace_id: str, invoice_id: str, data: dict) -> dict:
        """PATCH /v1/workspaces/{workspaceId}/invoices/{invoiceId}/status"""
        return self._patch(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/invoices/{invoice_id}/status",
            data,
            entity=f"invoice {invoice_id}",
        )

    def duplicate_invoice(self, workspace_id: str, invoice_id: str) -> dict:
        """POST /v1/workspaces/{workspaceId}/invoices/{invoiceId}/duplicate"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/invoices/{invoice_id}/duplicate",
            entity="invoice duplicate",
        )

    def list_invoice_payments(self, workspace_id: str, invoice_id: str, *, page: Optional[int] = None, page_size: Optional[int] = None) -> list:
        """GET /v1/workspaces/{workspaceId}/invoices/{invoiceId}/payments"""
        params: dict = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/invoices/{invoice_id}/payments",
            params=params or None,
            entity=f"invoice {invoice_id} payments",
        )
        return data if isinstance(data, list) else []

    def add_invoice_payment(self, workspace_id: str, invoice_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/invoices/{invoiceId}/payments"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/invoices/{invoice_id}/payments", data,
            entity="invoice payment",
        )

    def delete_invoice_payment(
        self, workspace_id: str, invoice_id: str, payment_id: str
    ) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/invoices/{invoiceId}/payments/{paymentId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/invoices/{invoice_id}/payments/{payment_id}",
            entity=f"invoice payment {payment_id}",
        )

    def get_invoice_settings(self, workspace_id: str) -> dict:
        """GET /v1/workspaces/{workspaceId}/invoices/settings"""
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/invoices/settings",
            entity="invoice settings",
        )

    def update_invoice_settings(self, workspace_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/invoices/settings"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/invoices/settings", data
        )

    def export_invoice(self, workspace_id: str, invoice_id: str, *, user_locale: Optional[str] = None) -> bytes:
        """GET /v1/workspaces/{workspaceId}/invoices/{invoiceId}/export (binary)"""
        params: dict = {}
        if user_locale:
            params["userLocale"] = user_locale
        return self._request(  # type: ignore[attr-defined]
            "GET",
            self._url(f"/workspaces/{workspace_id}/invoices/{invoice_id}/export"),  # type: ignore[attr-defined]
            params=params or None,
            entity=f"invoice export {invoice_id}",
            raw=True,
        )

    def filter_invoices(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/invoices/info"""
        return self._post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/invoices/info", data,
            entity="invoice filter",
        )
