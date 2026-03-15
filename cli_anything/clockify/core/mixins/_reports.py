from __future__ import annotations

from typing import Optional


class ReportsMixin:
    def report_detailed(
        self,
        workspace_id: str,
        start: str,
        end: str,
        project_ids: Optional[list] = None,
        user_ids: Optional[list] = None,
        client_ids: Optional[list] = None,
        tag_ids: Optional[list] = None,
        billable: Optional[bool] = None,
        description: Optional[str] = None,
        approval_state: Optional[str] = None,
        invoicing_state: Optional[str] = None,
        sort_column: Optional[str] = None,
        sort_order: Optional[str] = None,
        export_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        task_ids: Optional[list] = None,
        user_group_ids: Optional[list] = None,
        archived: Optional[bool] = None,
        amount_shown: Optional[str] = None,
        rounding: Optional[bool] = None,
        timezone: Optional[str] = None,
    ) -> dict:
        """POST /v1/workspaces/{workspaceId}/reports/detailed"""
        from cli_anything.clockify.utils.time_utils import to_iso_ms
        detailed_filter: dict = {"page": page, "pageSize": page_size}
        if sort_column:
            detailed_filter["sortColumn"] = sort_column
        body: dict = {
            "dateRangeStart": to_iso_ms(start),
            "dateRangeEnd": to_iso_ms(end),
            "detailedFilter": detailed_filter,
        }
        if project_ids:
            body["projects"] = {"ids": project_ids, "contains": "CONTAINS"}
        if user_ids:
            body["users"] = {"ids": user_ids, "contains": "CONTAINS"}
        if client_ids:
            body["clients"] = {"ids": client_ids, "contains": "CONTAINS"}
        if tag_ids:
            body["tags"] = {"ids": tag_ids, "contains": "CONTAINS"}
        if billable is not None:
            body["billable"] = billable
        if description:
            body["description"] = description
        if approval_state:
            body["approvalState"] = approval_state
        if invoicing_state:
            body["invoicingState"] = invoicing_state
        if sort_order:
            body["sortOrder"] = sort_order
        if export_type:
            body["exportType"] = export_type
        if task_ids:
            body["tasks"] = {"ids": task_ids, "contains": "CONTAINS"}
        if user_group_ids:
            body["userGroups"] = {"ids": user_group_ids, "contains": "CONTAINS"}
        if archived:
            body["archived"] = "All"
        if amount_shown:
            body["amountShown"] = amount_shown
        if rounding is not None:
            body["rounding"] = rounding
        if timezone:
            body["timeZone"] = timezone
        return self._reports_post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/reports/detailed", body
        )

    def report_summary(
        self,
        workspace_id: str,
        start: str,
        end: str,
        group_by: str = "PROJECT",
        sort_column: Optional[str] = None,
        billable: Optional[bool] = None,
        project_ids: Optional[list] = None,
        user_ids: Optional[list] = None,
        client_ids: Optional[list] = None,
        tag_ids: Optional[list] = None,
        description: Optional[str] = None,
        approval_state: Optional[str] = None,
        invoicing_state: Optional[str] = None,
        export_type: Optional[str] = None,
        sort_order: Optional[str] = None,
        task_ids: Optional[list] = None,
        user_group_ids: Optional[list] = None,
        archived: Optional[bool] = None,
        amount_shown: Optional[str] = None,
        rounding: Optional[bool] = None,
        timezone: Optional[str] = None,
    ) -> dict:
        """POST /v1/workspaces/{workspaceId}/reports/summary"""
        from cli_anything.clockify.utils.time_utils import to_iso_ms
        summary_filter: dict = {"groups": [group_by]}
        if sort_column:
            summary_filter["sortColumn"] = sort_column
        body: dict = {
            "dateRangeStart": to_iso_ms(start),
            "dateRangeEnd": to_iso_ms(end),
            "summaryFilter": summary_filter,
        }
        if project_ids:
            body["projects"] = {"ids": project_ids, "contains": "CONTAINS"}
        if user_ids:
            body["users"] = {"ids": user_ids, "contains": "CONTAINS"}
        if client_ids:
            body["clients"] = {"ids": client_ids, "contains": "CONTAINS"}
        if tag_ids:
            body["tags"] = {"ids": tag_ids, "contains": "CONTAINS"}
        if billable is not None:
            body["billable"] = billable
        if description:
            body["description"] = description
        if approval_state:
            body["approvalState"] = approval_state
        if invoicing_state:
            body["invoicingState"] = invoicing_state
        if export_type:
            body["exportType"] = export_type
        if sort_order:
            body["sortOrder"] = sort_order
        if task_ids:
            body["tasks"] = {"ids": task_ids, "contains": "CONTAINS"}
        if user_group_ids:
            body["userGroups"] = {"ids": user_group_ids, "contains": "CONTAINS"}
        if archived:
            body["archived"] = "All"
        if amount_shown:
            body["amountShown"] = amount_shown
        if rounding is not None:
            body["rounding"] = rounding
        if timezone:
            body["timeZone"] = timezone
        return self._reports_post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/reports/summary", body
        )

    def report_weekly(
        self,
        workspace_id: str,
        start: str,
        end: str,
        group: str = "USER",
        subgroup: str = "TIME",
        billable: Optional[bool] = None,
        project_ids: Optional[list] = None,
        user_ids: Optional[list] = None,
        client_ids: Optional[list] = None,
        tag_ids: Optional[list] = None,
        description: Optional[str] = None,
        approval_state: Optional[str] = None,
        invoicing_state: Optional[str] = None,
        export_type: Optional[str] = None,
        sort_order: Optional[str] = None,
        task_ids: Optional[list] = None,
        user_group_ids: Optional[list] = None,
        archived: Optional[bool] = None,
        amount_shown: Optional[str] = None,
        rounding: Optional[bool] = None,
        timezone: Optional[str] = None,
    ) -> dict:
        """POST /v1/workspaces/{workspaceId}/reports/weekly"""
        from cli_anything.clockify.utils.time_utils import to_iso_ms
        body: dict = {
            "dateRangeStart": to_iso_ms(start),
            "dateRangeEnd": to_iso_ms(end),
            "weeklyFilter": {"group": group, "subgroup": subgroup},
        }
        if project_ids:
            body["projects"] = {"ids": project_ids, "contains": "CONTAINS"}
        if user_ids:
            body["users"] = {"ids": user_ids, "contains": "CONTAINS"}
        if client_ids:
            body["clients"] = {"ids": client_ids, "contains": "CONTAINS"}
        if tag_ids:
            body["tags"] = {"ids": tag_ids, "contains": "CONTAINS"}
        if billable is not None:
            body["billable"] = billable
        if description:
            body["description"] = description
        if approval_state:
            body["approvalState"] = approval_state
        if invoicing_state:
            body["invoicingState"] = invoicing_state
        if export_type:
            body["exportType"] = export_type
        if sort_order:
            body["sortOrder"] = sort_order
        if task_ids:
            body["tasks"] = {"ids": task_ids, "contains": "CONTAINS"}
        if user_group_ids:
            body["userGroups"] = {"ids": user_group_ids, "contains": "CONTAINS"}
        if archived:
            body["archived"] = "All"
        if amount_shown:
            body["amountShown"] = amount_shown
        if rounding is not None:
            body["rounding"] = rounding
        if timezone:
            body["timeZone"] = timezone
        return self._reports_post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/reports/weekly", body
        )

    def report_attendance(
        self,
        workspace_id: str,
        start: str,
        end: str,
        *,
        approval_state: Optional[str] = None,
        billable: Optional[bool] = None,
        sort_column: Optional[str] = None,
        sort_order: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        export_type: Optional[str] = None,
        user_ids: Optional[list] = None,
        user_group_ids: Optional[list] = None,
        project_ids: Optional[list] = None,
        client_ids: Optional[list] = None,
        tag_ids: Optional[list] = None,
        task_ids: Optional[list] = None,
        description: Optional[str] = None,
        archived: Optional[bool] = None,
        rounding: Optional[bool] = None,
        timezone: Optional[str] = None,
    ) -> dict:
        """POST /v1/workspaces/{workspaceId}/reports/attendance"""
        from cli_anything.clockify.utils.time_utils import to_iso_ms
        body: dict = {
            "dateRangeStart": to_iso_ms(start),
            "dateRangeEnd": to_iso_ms(end),
        }
        if approval_state:
            body["approvalState"] = approval_state
        if billable is not None:
            body["billable"] = billable
        if export_type:
            body["exportType"] = export_type
        if sort_order:
            body["sortOrder"] = sort_order
        attendance_filter: dict = {}
        if sort_column:
            attendance_filter["sortColumn"] = sort_column
        if page is not None:
            attendance_filter["page"] = page
        if page_size is not None:
            attendance_filter["pageSize"] = page_size
        if attendance_filter:
            body["attendanceFilter"] = attendance_filter
        if user_ids:
            body["users"] = {"ids": user_ids, "contains": "CONTAINS"}
        if user_group_ids:
            body["userGroups"] = {"ids": user_group_ids, "contains": "CONTAINS"}
        if project_ids:
            body["projects"] = {"ids": project_ids, "contains": "CONTAINS"}
        if client_ids:
            body["clients"] = {"ids": client_ids, "contains": "CONTAINS"}
        if tag_ids:
            body["tags"] = {"ids": tag_ids, "contains": "CONTAINS"}
        if task_ids:
            body["tasks"] = {"ids": task_ids, "contains": "CONTAINS"}
        if description:
            body["description"] = description
        if archived:
            body["archived"] = "All"
        if rounding is not None:
            body["rounding"] = rounding
        if timezone:
            body["timeZone"] = timezone
        return self._reports_post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/reports/attendance", body
        )

    def report_expense(
        self,
        workspace_id: str,
        start: str,
        end: str,
        *,
        approval_state: Optional[str] = None,
        billable: Optional[bool] = None,
        sort_column: Optional[str] = None,
        sort_order: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        invoicing_state: Optional[str] = None,
        export_type: Optional[str] = None,
        user_ids: Optional[list] = None,
        user_group_ids: Optional[list] = None,
        project_ids: Optional[list] = None,
        client_ids: Optional[list] = None,
        task_ids: Optional[list] = None,
        category_ids: Optional[list] = None,
        timezone: Optional[str] = None,
    ) -> dict:
        """POST /v1/workspaces/{workspaceId}/reports/expenses/detailed"""
        from cli_anything.clockify.utils.time_utils import to_iso_ms
        body: dict = {
            "dateRangeStart": to_iso_ms(start),
            "dateRangeEnd": to_iso_ms(end),
        }
        if approval_state:
            body["approvalState"] = approval_state
        if billable is not None:
            body["billable"] = billable
        if sort_column:
            body["sortColumn"] = sort_column
        if sort_order:
            body["sortOrder"] = sort_order
        if page is not None:
            body["page"] = page
        if page_size is not None:
            body["pageSize"] = page_size
        if invoicing_state:
            body["invoicingState"] = invoicing_state
        if export_type:
            body["exportType"] = export_type
        if user_ids:
            body["users"] = {"ids": user_ids, "contains": "CONTAINS"}
        if user_group_ids:
            body["userGroups"] = {"ids": user_group_ids, "contains": "CONTAINS"}
        if project_ids:
            body["projects"] = {"ids": project_ids, "contains": "CONTAINS"}
        if client_ids:
            body["clients"] = {"ids": client_ids, "contains": "CONTAINS"}
        if task_ids:
            body["tasks"] = {"ids": task_ids, "contains": "CONTAINS"}
        if category_ids:
            body["categories"] = {"ids": category_ids, "contains": "CONTAINS"}
        if timezone:
            body["timeZone"] = timezone
        return self._reports_post(  # type: ignore[attr-defined]
            f"/workspaces/{workspace_id}/reports/expenses/detailed", body
        )
