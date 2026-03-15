"""Clockify API backend — wraps the Clockify REST API v1.

This is the only module that makes network requests.

Auth header: X-Api-Key  (NOT Authorization, NOT X-Addon-Token)
Pagination:  page + page-size query params; Last-Page response header.
Reports:     POST to reports_url (separate domain from base_url).
"""

from __future__ import annotations

from .mixins._base import _BackendBase, ClockifyAPIError
from .mixins._timer import TimerMixin
from .mixins._entries import EntriesMixin
from .mixins._projects import ProjectsMixin
from .mixins._tasks import TasksMixin
from .mixins._catalog import ClientsMixin, TagsMixin
from .mixins._users import UsersMixin
from .mixins._workspaces import WorkspacesMixin
from .mixins._reports import ReportsMixin
from .mixins._webhooks import WebhooksMixin
from .mixins._invoices import InvoicesMixin
from .mixins._expenses import ExpensesMixin
from .mixins._approval import ApprovalsMixin
from .mixins._time_off import TimeOffMixin
from .mixins._scheduling import SchedulingMixin
from .mixins._shared_reports import SharedReportsMixin
from .mixins._misc import GroupsMixin, HolidaysMixin, CustomFieldsMixin, EntitiesMixin


class ClockifyBackend(
    _BackendBase,
    TimerMixin,
    EntriesMixin,
    ProjectsMixin,
    TasksMixin,
    ClientsMixin,
    TagsMixin,
    UsersMixin,
    WorkspacesMixin,
    ReportsMixin,
    WebhooksMixin,
    InvoicesMixin,
    ExpensesMixin,
    ApprovalsMixin,
    TimeOffMixin,
    SchedulingMixin,
    SharedReportsMixin,
    GroupsMixin,
    HolidaysMixin,
    CustomFieldsMixin,
    EntitiesMixin,
):
    """All Clockify REST API calls, organised by resource type."""
    pass


__all__ = ["ClockifyBackend", "ClockifyAPIError"]
