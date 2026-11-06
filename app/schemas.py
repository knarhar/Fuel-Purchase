from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

Money = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
Name = Annotated[str, Field(min_length=1, max_length=100)]


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
