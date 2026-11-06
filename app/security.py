import hashlib
import secrets

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Admin, User


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def generate_key() -> str:
    return secrets.token_urlsafe(32)


# Dependencies
def require_admin(
    x_admin_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Admin:
    if not x_admin_key:
        raise HTTPException(401, "Missing admin API key.")
    admin = db.scalar(select(Admin).where(Admin.api_key_hash == hash_key(x_admin_key)))
    if admin is None:
        raise HTTPException(403, "Invalid admin API key.")
    return admin
