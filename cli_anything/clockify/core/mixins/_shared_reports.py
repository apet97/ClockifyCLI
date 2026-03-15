from __future__ import annotations

from typing import Optional


class SharedReportsMixin:
    def list_shared_reports(self, workspace_id: str, *, shared_reports_filter: Optional[str] = None) -> list:
        """GET /v1/workspaces/{workspaceId}/shared-reports"""
        params: dict = {}
        if shared_reports_filter:
            params["sharedReportsFilter"] = shared_reports_filter
        data = self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/shared-reports",
            params=params or None,
            entity="shared report",
        )
        return data if isinstance(data, list) else []

    def create_shared_report(self, workspace_id: str, data: dict) -> dict:
        """POST /v1/workspaces/{workspaceId}/shared-reports"""
        return self._post(f"/workspaces/{workspace_id}/shared-reports", data, entity="shared report")  # type: ignore[attr-defined]

    def update_shared_report(self, workspace_id: str, report_id: str, data: dict) -> dict:
        """PUT /v1/workspaces/{workspaceId}/shared-reports/{reportId}"""
        return self._put(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/shared-reports/{report_id}",
            data,
            entity=f"shared report {report_id}",
        )

    def delete_shared_report(self, workspace_id: str, report_id: str) -> dict:
        """DELETE /v1/workspaces/{workspaceId}/shared-reports/{reportId}"""
        return self._delete(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/shared-reports/{report_id}",
            entity=f"shared report {report_id}",
        )

    def get_shared_report(
        self,
        workspace_id: str,
        report_id: str,
        *,
        date_range_start: Optional[str] = None,
        date_range_end: Optional[str] = None,
        sort_column: Optional[str] = None,
        sort_order: Optional[str] = None,
        export_type: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> dict:
        """GET /v1/workspaces/{workspaceId}/shared-reports/{reportId}"""
        params: dict = {}
        if date_range_start:
            params["dateRangeStart"] = date_range_start
        if date_range_end:
            params["dateRangeEnd"] = date_range_end
        if sort_column:
            params["sortColumn"] = sort_column
        if sort_order:
            params["sortOrder"] = sort_order
        if export_type:
            params["exportType"] = export_type
        if page is not None:
            params["page"] = str(page)
        if page_size is not None:
            params["page-size"] = str(page_size)
        return self._get(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/shared-reports/{report_id}",
            params=params or None,
            entity=f"shared report {report_id}",
        )

    def get_public_shared_report(
        self,
        report_id: str,
        *,
        dateRangeStart: Optional[str] = None,
        dateRangeEnd: Optional[str] = None,
        sortOrder: Optional[str] = None,
        sortColumn: Optional[str] = None,
        exportType: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> dict:
        """GET /v1/shared-reports/{id} (reports domain)"""
        params: dict = {}
        if dateRangeStart:
            params["dateRangeStart"] = dateRangeStart
        if dateRangeEnd:
            params["dateRangeEnd"] = dateRangeEnd
        if sortOrder:
            params["sortOrder"] = sortOrder
        if sortColumn:
            params["sortColumn"] = sortColumn
        if exportType:
            params["exportType"] = exportType
        if page is not None:
            params["page"] = str(page)
        if page_size is not None:
            params["page-size"] = str(page_size)
        return self._request("GET", self._reports_url(f"/shared-reports/{report_id}"),  # type: ignore[attr-defined]
                             params=params or None, entity=f"public report {report_id}")
