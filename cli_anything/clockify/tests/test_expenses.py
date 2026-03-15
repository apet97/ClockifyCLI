"""Tests for expense operations."""

from __future__ import annotations

import json as jsonlib
import responses

from cli_anything.clockify.tests.conftest import (
    BASE_URL, WS_ID, USER_ID,
)

EXPENSES_URL = f"{BASE_URL}/workspaces/{WS_ID}/expenses"
CATEGORIES_URL = f"{BASE_URL}/workspaces/{WS_ID}/expenses/categories"


def make_expense(
    expense_id: str = "exp1111111111111111111111",
    category_name: str = "Travel",
    amount: float = 50.0,
) -> dict:
    return {
        "id": expense_id,
        "categoryName": category_name,
        "quantity": 1,
        "unitPrice": amount,
        "date": "2026-03-13T00:00:00Z",
        "notes": "",
        "workspaceId": WS_ID,
        "userId": USER_ID,
    }


def make_category(
    cat_id: str = "cat1111111111111111111111",
    name: str = "Travel",
) -> dict:
    return {"id": cat_id, "name": name, "unit": "", "workspaceId": WS_ID}


@responses.activate
def test_list_expenses(backend):
    """list_expenses returns all expenses."""
    expenses = [make_expense("e1"), make_expense("e2")]
    responses.add(
        responses.GET, EXPENSES_URL,
        json=expenses, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )
    result = backend.list_expenses(WS_ID)
    assert len(result) == 2


@responses.activate
def test_create_expense(backend):
    """create_expense POSTs to expenses URL."""
    expense = make_expense()
    responses.add(responses.POST, EXPENSES_URL, json=expense, status=201)
    result = backend.create_expense(WS_ID, {
        "categoryId": "cat1111111111111111111111",
        "quantity": 1,
        "unitPrice": 50.0,
        "date": "2026-03-13T00:00:00Z",
    })
    assert result["id"] == expense["id"]


@responses.activate
def test_get_expense(backend):
    """get_expense fetches by ID."""
    expense = make_expense()
    responses.add(responses.GET, f"{EXPENSES_URL}/{expense['id']}", json=expense, status=200)
    result = backend.get_expense(WS_ID, expense["id"])
    assert result["id"] == expense["id"]


@responses.activate
def test_delete_expense(backend):
    """delete_expense sends DELETE to correct URL."""
    expense_id = "exp1111111111111111111111"
    responses.add(responses.DELETE, f"{EXPENSES_URL}/{expense_id}", json={}, status=200)
    backend.delete_expense(WS_ID, expense_id)
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_list_expense_categories(backend):
    """list_expense_categories returns categories."""
    cats = [make_category("c1", "Travel"), make_category("c2", "Food")]
    responses.add(responses.GET, CATEGORIES_URL, json=cats, status=200)
    result = backend.list_expense_categories(WS_ID)
    assert len(result) == 2
    assert result[0]["name"] == "Travel"


@responses.activate
def test_create_expense_category(backend):
    """create_expense_category POSTs to categories URL."""
    cat = make_category()
    responses.add(responses.POST, CATEGORIES_URL, json=cat, status=201)
    result = backend.create_expense_category(WS_ID, {"name": "Travel"})
    assert result["id"] == cat["id"]


@responses.activate
def test_delete_expense_category(backend):
    """delete_expense_category sends DELETE."""
    cat_id = "cat1111111111111111111111"
    responses.add(responses.DELETE, f"{CATEGORIES_URL}/{cat_id}", json={}, status=200)
    backend.delete_expense_category(WS_ID, cat_id)
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_cli_expenses_list_json(runner, session):
    """expenses list --json returns JSON array."""
    from cli_anything.clockify.clockify_cli import main
    import json

    expenses = [make_expense()]
    responses.add(
        responses.GET, EXPENSES_URL,
        json=expenses, status=200,
        headers={"Last-Page": "true"},
        match_querystring=False,
    )

    result = runner.invoke(main, [
        "--api-key", session.api_key,
        "--workspace", WS_ID,
        "expenses", "list", "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["categoryName"] == "Travel"
