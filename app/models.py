from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price_per_litre >= 0"),
        CheckConstraint("available_litres >= 0"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price_per_litre: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    available_litres: Mapped[Decimal] = mapped_column(Numeric(12, 2))


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("account_balance >= 0"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(50), unique=True)
    birthdate: Mapped[date]
    account_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    api_key_hash: Mapped[str] = mapped_column(String(64), unique=True)


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    litres: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    product: Mapped[Product] = relationship()