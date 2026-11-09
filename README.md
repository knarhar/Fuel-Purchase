# Fuel Purchase API


## Installation
Add environment variables:
```bash
cp .env.sample .env
```

Create virtual environment and install packages:
```
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run app:
```
uvicorn app.main:app --reload
```

## Create an admin

```bash
python -m scripts.create_admin <username>
```
This prints an API key once. Save it, because it can't be shown again.
Send it in the `X-Admin-Key` header to use the `/api/admin/...` endpoints.

Only the SHA-256 hash of the key is stored. The key is a random 32-byte token,
so a slow password hasher isn't needed, and the hash can be looked up directly.

## Run tests

```bash
pytest
```

Covered cases:
- Successful purchase: response, balance and stock deduction, history
- Buying exactly the full balance and stock
- Insufficient balance and not enough fuel: balance, stock and history stay unchanged
- Purchase history only shows the user's own purchases
- Invalid litres (zero, negative, not a number)
- Missing or unknown username, unknown product
- Missing or invalid admin API key
- Duplicate username
- Null values rejected in admin updates

## Endpoints

Interactive docs: http://127.0.0.1:8000/docs

| Method | Endpoint | Header | Description |
|---|---|---|---|
| POST | `/api/admin/products/` | `X-Admin-Key` | Create a fuel product |
| PATCH | `/api/admin/products/{product_id}/` | `X-Admin-Key` | Update product name, price or stock |
| POST | `/api/admin/users/` | `X-Admin-Key` | Create a user |
| PATCH | `/api/admin/users/{user_id}/` | `X-Admin-Key` | Update user info or account balance |
| POST | `/api/purchases/` | `X-Username` | Purchase fuel |
| GET | `/api/purchases/` | `X-Username` | Get the user's purchase history |

## Example

```bash
curl -X POST http://127.0.0.1:8000/api/admin/products/ \
  -H "X-Admin-Key: <admin-api-key>" -H "Content-Type: application/json" \
  -d '{"name": "Petrol 95", "price_per_litre": "500.00", "available_litres": "1000"}'

curl -X POST http://127.0.0.1:8000/api/admin/users/ \
  -H "X-Admin-Key: <admin-api-key>" -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", "username": "john", "birthdate": "1990-01-01", "account_balance": "10000.00"}'

curl -X POST http://127.0.0.1:8000/api/purchases/ \
  -H "X-Username: john" -H "Content-Type: application/json" \
  -d '{"product_id": 1, "litres": 10}'

curl http://127.0.0.1:8000/api/purchases/ -H "X-Username: john"
```

Errors are returned as `{"error": "<message>"}`.