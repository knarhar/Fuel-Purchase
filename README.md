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