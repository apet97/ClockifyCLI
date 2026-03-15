"""Spec-driven parity checks against the bundled OpenAPI document."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import yaml


HTTP_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")
DOCSTRING_OPERATION_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\s+(/v1/\S+)")
ROOT = Path(__file__).resolve().parents[3]
SPEC_PATH = ROOT / "openapi.cleaned 2.yaml"
MIXINS_DIR = ROOT / "cli_anything" / "clockify" / "core" / "mixins"


def _normalize_path(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "{}", path.split("?", 1)[0])


def _spec_operations() -> set[tuple[str, str]]:
    spec = yaml.safe_load(SPEC_PATH.read_text())
    operations: set[tuple[str, str]] = set()
    for path, item in spec["paths"].items():
        for method in HTTP_METHODS:
            if method.lower() in item:
                operations.add((method, _normalize_path(path)))
    return operations


def _backend_operations() -> set[tuple[str, str]]:
    operations: set[tuple[str, str]] = set()
    for path in sorted(MIXINS_DIR.glob("*.py")):
        module = ast.parse(path.read_text())
        for node in module.body:
            if not isinstance(node, ast.ClassDef):
                continue
            for fn in node.body:
                if not isinstance(fn, ast.FunctionDef):
                    continue
                docstring = ast.get_docstring(fn) or ""
                for method, doc_path in DOCSTRING_OPERATION_RE.findall(docstring):
                    operations.add((method, _normalize_path(doc_path)))
    return operations


def test_backend_operations_match_openapi_spec():
    """Every documented backend operation should match the bundled OpenAPI spec."""
    spec_operations = _spec_operations()
    backend_operations = _backend_operations()

    missing = sorted(spec_operations - backend_operations)
    extra = sorted(backend_operations - spec_operations)

    assert not missing and not extra, (
        "OpenAPI/backend parity mismatch\n"
        f"Missing: {missing}\n"
        f"Extra: {extra}"
    )
