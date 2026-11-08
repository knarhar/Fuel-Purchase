from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PastDate

Money = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
Name = Annotated[str, Field(min_length=1, max_length=100)]
Username = Annotated[str, Field(min_length=1, max_length=50)]


class ProductCreate(BaseModel):
    name: Name
    price_per_litre: Money
    available_litres: Money


class ProductUpdate(BaseModel):
    name: Name | None = None
    price_per_litre: Money | None = None
    available_litres: Money | None = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price_per_litre: Decimal
    available_litres: Decimal


class UserCreate(BaseModel):
    first_name: Name
    last_name: Name
    username: Username
    birthdate: PastDate
    account_balance: Money = Decimal("0.00")


class UserUpdate(BaseModel):
    first_name: Name | None = None
    last_name: Name | None = None
    username: Username | None = None
    birthdate: PastDate | None = None
    account_balance: Money | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    username: str
    birthdate: date
    account_balance: Decimal
