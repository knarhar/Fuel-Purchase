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
