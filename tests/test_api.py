import os
from decimal import Decimal

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Admin, Product, User
from app.security import hash_key

ADMIN_KEY = "test-admin-key"
ADMIN = {"X-Admin-Key": ADMIN_KEY}
JOHN = {"X-Username": "john"}


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with SessionLocal() as db:
        db.add(
            Admin(
                username="admin",
                api_key_hash=hash_key(ADMIN_KEY)
            )
        )
        db.commit()

    with TestClient(app) as test_client:
        yield test_client

def setup_data(client, balance="10000.00"):
    product = client.post(
        "/api/admin/products/",
        json={"name": "Petrol 95", "price_per_litre": "500.00", "available_litres": "1000"},
        headers=ADMIN,
    ).json()
    client.post(
        "/api/admin/users/",
        json={"first_name": "John", "last_name": "Doe", "username": "john",
              "birthdate": "1990-01-01", "account_balance": balance},
        headers=ADMIN,
    )
    return product["id"]


def balance_and_stock(product_id, username="john"):
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == username))
        return user.account_balance, db.get(Product, product_id).available_litres


def test_purchase_success(client):
    product_id = setup_data(client)
    r = client.post("/api/purchases/", json={"product_id": product_id, "litres": 10}, headers=JOHN)
    assert r.status_code == 201
    assert r.json() == {
        "id": 1, "product": "Petrol 95", "litres": "10.00", "total_price": "5000.00",
        "remaining_balance": "5000.00", "remaining_stock_litres": "990.00",
    }
    history = client.get("/api/purchases/", headers=JOHN).json()
    assert len(history) == 1
    assert history[0]["created_at"].endswith("Z")


def test_buy_entire_balance_and_stock(client):
    product_id = setup_data(client, balance="0.30")
    client.patch(f"/api/admin/products/{product_id}/", json={"price_per_litre": "0.10", "available_litres": "3"}, headers=ADMIN)
    for litres in [1, 2]:
        r = client.post("/api/purchases/", json={"product_id": product_id, "litres": litres}, headers=JOHN)
        assert r.status_code == 201
    assert r.json()["remaining_balance"] == "0.00"
    assert r.json()["remaining_stock_litres"] == "0.00"


def test_null_update_rejected(client):
    product_id = setup_data(client)
    r = client.patch(f"/api/admin/products/{product_id}/", json={"name": None}, headers=ADMIN)
    assert r.status_code == 422
    r = client.patch("/api/admin/users/1/", json={"account_balance": None}, headers=ADMIN)
    assert r.status_code == 422


def test_insufficient_balance_changes_nothing(client):
    product_id = setup_data(client, balance="100.00")
    r = client.post("/api/purchases/", json={"product_id": product_id, "litres": 10}, headers=JOHN)
    assert r.status_code == 400
    assert r.json() == {"error": "Insufficient balance."}
    assert balance_and_stock(product_id) == (Decimal("100.00"), Decimal("1000.00"))
    assert client.get("/api/purchases/", headers=JOHN).json() == []


def test_not_enough_fuel_changes_nothing(client):
    product_id = setup_data(client)
    r = client.post("/api/purchases/", json={"product_id": product_id, "litres": 2000}, headers=JOHN)
    assert r.status_code == 400
    assert r.json() == {"error": "Not enough fuel available."}
    assert balance_and_stock(product_id) == (Decimal("10000.00"), Decimal("1000.00"))
    assert client.get("/api/purchases/", headers=JOHN).json() == []


def test_history_shows_only_own_purchases(client):
    product_id = setup_data(client)
    client.post(
        "/api/admin/users/",
        json={"first_name": "Jane", "last_name": "Doe", "username": "jane",
              "birthdate": "1992-01-01", "account_balance": "10000.00"},
        headers=ADMIN,
    )
    client.post("/api/purchases/", json={"product_id": product_id, "litres": 10}, headers=JOHN)
    client.post("/api/purchases/", json={"product_id": product_id, "litres": 2}, headers={"X-Username": "jane"})

    john_history = client.get("/api/purchases/", headers=JOHN).json()
    assert len(john_history) == 1
    assert john_history[0]["litres"] == "10.00"
    jane_history = client.get("/api/purchases/", headers={"X-Username": "jane"}).json()
    assert len(jane_history) == 1
    assert jane_history[0]["litres"] == "2.00"


def test_bad_litres(client):
    product_id = setup_data(client)
    for litres in [0, -5, "abc"]:
        r = client.post("/api/purchases/", json={"product_id": product_id, "litres": litres}, headers=JOHN)
        assert r.status_code == 422


def test_missing_and_unknown_user(client):
    product_id = setup_data(client)
    body = {"product_id": product_id, "litres": 1}
    assert client.post("/api/purchases/", json=body).status_code == 400
    assert client.post("/api/purchases/", json=body, headers={"X-Username": "nobody"}).status_code == 404


def test_unknown_product(client):
    setup_data(client)
    r = client.post("/api/purchases/", json={"product_id": 999, "litres": 1}, headers=JOHN)
    assert r.status_code == 404


def test_admin_key_required(client):
    body = {"name": "Diesel", "price_per_litre": "400", "available_litres": "100"}
    assert client.post("/api/admin/products/", json=body).status_code == 401
    assert client.post("/api/admin/products/", json=body, headers={"X-Admin-Key": "wrong"}).status_code == 403


def test_duplicate_username(client):
    setup_data(client)
    r = client.post(
        "/api/admin/users/",
        json={"first_name": "J", "last_name": "D", "username": "john", "birthdate": "1990-01-01"},
        headers=ADMIN,
    )
    assert r.status_code == 409