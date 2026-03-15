"""Time utility helpers for the Clockify CLI.

All functions are pure (no I/O, no network) so they can be tested without mocks.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta

from dateutil import parser as dateutil_parser


def now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string ending in Z.

    Example: '2026-03-13T14:30:00Z'
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_iso_ms() -> str:
    """Return the current UTC time with milliseconds (for report request bodies).

    Example: '2026-03-13T14:30:00.000Z'
    """
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def to_iso_ms(iso: str) -> str:
    """Normalize any ISO 8601 string to millisecond format for report bodies.

    Example: '2026-03-01T00:00:00Z' → '2026-03-01T00:00:00.000Z'
    """
    try:
        dt = dateutil_parser.parse(iso)
    except (ValueError, Exception) as e:
        raise ValueError(f"Invalid ISO date '{iso}': {e}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def parse_date_arg(s: str) -> str:
    """Parse a date argument into ISO 8601 date string (YYYY-MM-DD).

    Accepts:
    - 'today'
    - 'yesterday'
    - 'YYYY-MM-DD'

    Returns: 'YYYY-MM-DD'
    """
    s = s.strip().lower()
    today = datetime.now(timezone.utc).date()
    if s == "today":
        return today.isoformat()
    if s == "yesterday":
        return (today - timedelta(days=1)).isoformat()
    # Try parsing as date
    try:
        dt = dateutil_parser.parse(s)
    except (ValueError, Exception) as e:
        raise ValueError(f"Invalid date '{s}': {e}")
    return dt.date().isoformat()


def parse_datetime_arg(s: str) -> str:
    """Parse a datetime argument into ISO 8601 UTC string ending in Z.

    Accepts:
    - 'HH:MM'           → today's date at that time (UTC)
    - 'YYYY-MM-DD HH:MM'
    - Full ISO 8601 (with or without timezone)

    Returns: 'YYYY-MM-DDTHH:MM:SSZ'
    """
    s = s.strip()
    # HH:MM shorthand → today at that time
    if re.match(r"^\d{1,2}:\d{2}$", s):
        today = datetime.now(timezone.utc).date().isoformat()
        s = f"{today}T{s}:00Z"
    try:
        dt = dateutil_parser.parse(s)
    except (ValueError, Exception) as e:
        raise ValueError(f"Invalid date/time '{s}': {e}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_duration_iso(s: str) -> int:
    """Parse a Clockify ISO 8601 duration string into seconds.

    Examples: 'PT8H30M0S' → 30600, 'P1DT2H' → 93600
    """
    pattern = re.compile(
        r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?",
        re.IGNORECASE,
    )
    m = pattern.match(s.strip())
    if not m:
        return 0
    days = int(m.group(1) or 0)
    hours = int(m.group(2) or 0)
    minutes = int(m.group(3) or 0)
    seconds = int(float(m.group(4) or 0))
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def format_duration_hms(secs: int) -> str:
    """Format seconds into H:MM:SS string.

    Example: 30600 → '8:30:00'
    """
    secs = max(0, int(secs))
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    return f"{h}:{m:02d}:{s:02d}"


def elapsed_since(start_iso: str) -> str:
    """Return a human-readable elapsed time since start_iso.

    Example: '2h 14m', '45m', '5s'
    """
    try:
        start = dateutil_parser.parse(start_iso)
    except (ValueError, Exception) as e:
        raise ValueError(f"Invalid start time '{start_iso}': {e}")
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - start
    total_secs = int(delta.total_seconds())
    if total_secs < 0:
        return "0s"
    h = total_secs // 3600
    m = (total_secs % 3600) // 60
    s = total_secs % 60
    parts = []
    if h:
        parts.append(f"{h}h")
    if m or h:
        parts.append(f"{m}m")
    if not parts:
        parts.append(f"{s}s")
    return " ".join(parts)


def date_range_today() -> tuple[str, str]:
    """Return (start, end) ISO strings covering today (UTC)."""
    today = datetime.now(timezone.utc).date()
    start = f"{today.isoformat()}T00:00:00Z"
    end = f"{today.isoformat()}T23:59:59Z"
    return start, end
