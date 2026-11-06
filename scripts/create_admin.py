import sys

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Admin
from app.security import generate_key, hash_key


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m scripts.create_admin <username>")
    username = sys.argv[1]

    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Admin).where(Admin.username == username)):
            sys.exit(f"Admin '{username}' already exists.")
        key = generate_key()
        db.add(Admin(username=username, api_key_hash=hash_key(key)))
        db.commit()

    print(f"Admin '{username}' created. Save this API key, it will not be shown again:")
    print(key)


if __name__ == "__main__":
    main()