"""Tests for invoice operations."""

from __future__ import annotations

import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, API_KEY,
)

INVOICES_URL = f"{BASE_URL}/workspaces/{WS_ID}/invoices"


def make_invoice(
    invoice_id: str = "inv1111111111111111111111",
    invoice_number: str = "INV-001",
    status: str = "DRAFT",
    client_name: str = "Acme Corp",
) -> dict:
    return {
        "id": invoice_id,
        "invoiceNumber": invoice_number,
        "status": status,
        "clientName": client_name,
        "total": 1000.0,
        "workspaceId": WS_ID,
    }


def make_payment(
    payment_id: str = "pay1111111111111111111111",
    amount: float = 500.0,
) -> dict:
    return {
        "id": payment_id,
        "amount": amount,
        "date": "2026-03-13T00:00:00Z",
        "note": "",
    }


@responses.activate
def test_list_invoices(backend):
    """list_invoices returns all invoices."""
    invoices = [make_invoice("i1"), make_invoice("i2")]
    responses.add(
        responses.GET, INVOICES_URL,
        json=invoices, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = backend.list_invoices(WS_ID)
    assert len(result) == 2


@responses.activate
def test_get_invoice(backend):
    """get_invoice fetches by ID."""
    inv = make_invoice()
    responses.add(responses.GET, f"{INVOICES_URL}/{inv['id']}", json=inv, status=200)
    result = backend.get_invoice(WS_ID, inv["id"])
    assert result["invoiceNumber"] == "INV-001"


@responses.activate
def test_create_invoice(backend):
    """create_invoice POSTs to invoices URL."""
    inv = make_invoice()
    responses.add(responses.POST, INVOICES_URL, json=inv, status=201)
    result = backend.create_invoice(WS_ID, {"clientId": "client111"})
    assert result["id"] == inv["id"]


@responses.activate
def test_change_invoice_status(backend):
    """change_invoice_status PATCHes the status endpoint."""
    inv = make_invoice(status="SENT")
    url = f"{INVOICES_URL}/{inv['id']}/status"
    responses.add(responses.PATCH, url, json=inv, status=200)
    result = backend.change_invoice_status(WS_ID, inv["id"], {"invoiceStatus": "SENT"})
    assert result["status"] == "SENT"


@responses.activate
def test_add_invoice_payment(backend):
    """add_invoice_payment POSTs to the payments endpoint."""
    inv = make_invoice()
    payment = make_payment()
    url = f"{INVOICES_URL}/{inv['id']}/payments"
    responses.add(responses.POST, url, json=payment, status=201)
    result = backend.add_invoice_payment(WS_ID, inv["id"], {
        "amount": 500.0,
        "date": "2026-03-13T00:00:00Z",
    })
    assert result["id"] == payment["id"]


@responses.activate
def test_list_invoice_payments(backend):
    """list_invoice_payments GETs the payments endpoint."""
    inv = make_invoice()
    payments = [make_payment()]
    url = f"{INVOICES_URL}/{inv['id']}/payments"
    responses.add(responses.GET, url, json=payments, status=200)
    result = backend.list_invoice_payments(WS_ID, inv["id"])
    assert len(result) == 1


@responses.activate
def test_cli_invoices_list_json(runner, session):
    """invoices list --json returns JSON array."""
    from cli_anything.clockify.clockify_cli import main
    import json

    invoices = [make_invoice()]
    responses.add(
        responses.GET, INVOICES_URL,
        json=invoices, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "invoices", "list", "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["invoiceNumber"] == "INV-001"


@responses.activate
def test_invoices_list_status_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, INVOICES_URL,
        json=[make_invoice(status="DRAFT")],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "invoices", "list", "--status", "SENT", "--json"])
    assert result.exit_code == 0, result.output
    assert "statuses=SENT" in responses.calls[0].request.url


@responses.activate
def test_invoices_list_sort_filter(runner):
    from cli_anything.clockify.clockify_cli import main
    responses.add(
        responses.GET, INVOICES_URL,
        json=[make_invoice()],
        status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = runner.invoke(main, ["--api-key", API_KEY, "--workspace", WS_ID, "invoices", "list", "--sort-column", "AMOUNT", "--sort-order", "DESCENDING", "--json"])
    assert result.exit_code == 0, result.output
    assert "sort-column=AMOUNT" in responses.calls[0].request.url
    assert "sort-order=DESCENDING" in responses.calls[0].request.url
