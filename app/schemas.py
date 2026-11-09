from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PastDate, model_validator

Money = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
Litres = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
PositiveLitres = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]

Name = Annotated[str, Field(min_length=1, max_length=100)]
Username = Annotated[str, Field(min_length=1, max_length=50)]


class UpdateModel(BaseModel):
    @model_validator(mode="after")
    def reject_nulls(self):
        nulls = [field for field in self.model_fields_set if getattr(self, field) is None]
        if nulls:
            raise ValueError(f"Fields cannot be null: {', '.join(sorted(nulls))}")
        return self


class ProductCreate(BaseModel):
    name: Name
    price_per_litre: Money
    available_litres: Litres


class ProductUpdate(UpdateModel):
    name: Name | None = None
    price_per_litre: Money | None = None
    available_litres: Litres | None = None


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


class UserUpdate(UpdateModel):
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


class PurchaseCreate(BaseModel):
    product_id: int
    litres: PositiveLitres


class PurchaseCreated(BaseModel):
    id: int
    product: str
    litres: PositiveLitres
    total_price: Money
    remaining_balance: Money
    remaining_stock_litres: Litres


class PurchaseOut(BaseModel):
    id: int
    product: str
    litres: Decimal
    total_price: Decimal
    created_at: datetime
