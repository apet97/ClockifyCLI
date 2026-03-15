"""Base class and HTTP helpers for the Clockify backend."""

from __future__ import annotations

import json as _json
import random
import sys
import time
from typing import Any, Optional

import requests

from cli_anything.clockify.utils.session import Session


class ClockifyAPIError(Exception):
    """Raised when the Clockify API returns an error response."""

    def __init__(self, status_code: int, message: str, body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.body = body

    def __str__(self) -> str:
        return f"HTTP {self.status_code}: {self.message}"


class _BackendBase:
    """Infrastructure: __init__ + all private HTTP helpers."""

    def __init__(self, session: Session):
        self.session = session
        self._http = requests.Session()
        self.extra_body: Optional[dict] = None
        self.verbose: bool = False
        self.debug: bool = False
        self.dry_run: bool = False
        self.timeout: int = 30
        self.reports_timeout: int = 60

        from requests.adapters import HTTPAdapter
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=0)
        self._http.mount("https://", adapter)
        self._http.mount("http://", adapter)

    def close(self) -> None:
        """Close the HTTP session and release connection pool resources."""
        self._http.close()

    # ── Private HTTP helpers ──────────────────────────────────────────

    def _headers(self) -> dict[str, str]:
        return {
            "X-Api-Key": self.session.api_key,
            "Content-Type": "application/json",
        }

    def _url(self, path: str) -> str:
        return f"{self.session.base_url}{path}"

    def _reports_url(self, path: str) -> str:
        return f"{self.session.reports_url}{path}"

    def _handle_response(self, resp: requests.Response, entity: str = "", raw: bool = False) -> Any:
        """Parse response, mapping HTTP errors to ClockifyAPIError."""
        if resp.status_code == 401:
            raise ClockifyAPIError(401, "Invalid API key. Check CLOCKIFY_API_KEY.")
        if resp.status_code == 403:
            raise ClockifyAPIError(
                403, "Permission denied. You may not have admin access."
            )
        if resp.status_code == 404:
            msg = f"Not found: {entity}" if entity else "Not found."
            raise ClockifyAPIError(404, msg)
        if resp.status_code == 429:
            # Caller handles retry
            raise ClockifyAPIError(429, "Rate limit exceeded.")
        if resp.status_code >= 500:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise ClockifyAPIError(resp.status_code, str(body), body)
        resp.raise_for_status()
        if raw:
            return resp.content
        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """Recursively merge override into base, returning base."""
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                _BackendBase._deep_merge(base[k], v)
            else:
                base[k] = v
        return base

    _MAX_RETRIES = 5

    _SENSITIVE_KEYS = {
        "api_key", "apiKey", "password", "token", "secret",
        "authorizationHeader", "accessToken", "refreshToken",
    }

    def _redact(self, data: Any) -> Any:
        """Redact sensitive fields from a dict for display."""
        if isinstance(data, dict):
            return {k: ("***" if k in self._SENSITIVE_KEYS else self._redact(v))
                    for k, v in data.items()}
        if isinstance(data, list):
            return [self._redact(item) for item in data]
        return data

    @staticmethod
    def _parse_retry_after(resp: requests.Response) -> float | None:
        """Parse Retry-After header as seconds (int) or HTTP-date."""
        header = resp.headers.get("Retry-After")
        if not header:
            return None
        try:
            return float(header)
        except ValueError:
            pass
        from email.utils import parsedate_to_datetime
        from datetime import datetime, timezone
        try:
            target = parsedate_to_datetime(header)
            return max(0.0, (target - datetime.now(timezone.utc)).total_seconds())
        except Exception:
            return None

    def _retry_request(self, fn):
        """Execute fn() with retry on 429 and network errors. Returns requests.Response."""
        last_exc = None
        for attempt in range(self._MAX_RETRIES + 1):
            retry_after = None
            try:
                resp = fn()
                if resp.status_code != 429 or attempt == self._MAX_RETRIES:
                    return resp
                retry_after = self._parse_retry_after(resp)
                last_exc = None
            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt == self._MAX_RETRIES:
                    raise ClockifyAPIError(0, f"Network error: {e}")
                last_exc = e
            delay = (2 ** attempt) + random.uniform(0, 0.5)
            if retry_after is not None:
                delay = max(delay, retry_after)
            time.sleep(delay)
        # Should not reach here, but handle gracefully
        if last_exc:
            raise ClockifyAPIError(0, f"Network error: {last_exc}")
        return resp  # type: ignore[possibly-undefined]

    def _log_rate_limit(self, resp: requests.Response) -> None:
        """Log rate-limit headers when verbose/debug mode is on."""
        if not (self.verbose or self.debug):
            return
        remaining = resp.headers.get("X-RateLimit-Remaining")
        limit = resp.headers.get("X-RateLimit-Limit")
        if remaining is not None:
            print(f"[clockify] rate-limit: {remaining}/{limit or '?'} remaining", file=sys.stderr)

    def _request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        json_data=None,
        entity: str = "",
        raw: bool = False,
    ) -> Any:
        if json_data is not None and self.extra_body:
            self._deep_merge(json_data, self.extra_body)
        # Dry-run: print request details and return without sending
        if self.dry_run:
            info: dict = {"method": method, "url": url}
            if params:
                info["params"] = params
            if json_data is not None:
                info["body"] = self._redact(json_data)
            print(_json.dumps(info, indent=2, default=str))
            return {}
        t0 = time.monotonic()
        resp = self._retry_request(
            lambda: self._http.request(
                method, url, headers=self._headers(),
                params=params, json=json_data, timeout=self.timeout,
            )
        )
        elapsed = time.monotonic() - t0
        if self.verbose or self.debug:
            print(f"[clockify] {method} {url} -> {resp.status_code} ({elapsed:.3f}s)", file=sys.stderr)
        self._log_rate_limit(resp)
        if self.debug and json_data is not None:
            print(f"[clockify] body: {_json.dumps(self._redact(json_data), default=str)}", file=sys.stderr)
        return self._handle_response(resp, entity, raw=raw)

    def _get(self, path: str, params: Optional[dict] = None, entity: str = "") -> Any:
        return self._request("GET", self._url(path), params=params, entity=entity)

    def _post(self, path: str, data: Optional[dict] = None, entity: str = "") -> Any:
        return self._request("POST", self._url(path), json_data=data, entity=entity)

    def _put(self, path: str, data: Optional[dict] = None, entity: str = "") -> Any:
        return self._request("PUT", self._url(path), json_data=data, entity=entity)

    def _patch(self, path: str, data: Optional[dict] = None, entity: str = "") -> Any:
        return self._request("PATCH", self._url(path), json_data=data, entity=entity)

    def _delete(self, path: str, entity: str = "") -> Any:
        return self._request("DELETE", self._url(path), entity=entity)

    _MAX_PAGES = 1000

    def _get_all_pages(
        self,
        path: str,
        params: Optional[dict] = None,
        page_size: int = 50,
        entity: str = "",
    ) -> list:
        """Fetch all pages of a paginated endpoint."""
        results: list = []
        page = 1
        base_params = dict(params or {})
        base_params["page-size"] = page_size
        url = self._url(path)

        while True:
            base_params["page"] = page
            t0 = time.monotonic()
            resp = self._retry_request(
                lambda: self._http.get(
                    url, headers=self._headers(),
                    params=base_params, timeout=self.timeout,
                )
            )
            elapsed = time.monotonic() - t0
            if self.verbose or self.debug:
                print(f"[clockify] GET {url} (page {page}) -> {resp.status_code} ({elapsed:.3f}s)", file=sys.stderr)
            self._log_rate_limit(resp)
            data = self._handle_response(resp, entity)
            if isinstance(data, list):
                results.extend(data)
            elif isinstance(data, dict):
                # Some endpoints return {data: [...]}
                items = data.get("data") or data.get("items") or []
                results.extend(items)
            last_page = resp.headers.get("Last-Page", "false").lower() == "true"
            if last_page or not data:
                break
            page += 1
            if page > self._MAX_PAGES:
                print(
                    f"[clockify] warning: pagination stopped at {self._MAX_PAGES} pages "
                    f"({len(results)} items). Results may be incomplete.",
                    file=sys.stderr,
                )
                break
        return results

    def _reports_post(self, path: str, body: dict) -> dict:
        """POST to the reports API (separate domain)."""
        if self.extra_body:
            self._deep_merge(body, self.extra_body)
        url = self._reports_url(path)
        t0 = time.monotonic()
        resp = self._retry_request(
            lambda: self._http.post(
                url, headers=self._headers(), json=body, timeout=self.reports_timeout,
            )
        )
        elapsed = time.monotonic() - t0
        if self.verbose or self.debug:
            print(f"[clockify] POST {url} -> {resp.status_code} ({elapsed:.3f}s)", file=sys.stderr)
        self._log_rate_limit(resp)
        return self._handle_response(resp, "report")
