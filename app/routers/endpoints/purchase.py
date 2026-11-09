from datetime import timezone
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import User, Product, Purchase
from app.schemas import PurchaseCreated, PurchaseCreate, PurchaseOut
from app.security import get_current_user

router = APIRouter(tags=["Purchases"])


@router.post("/", response_model=PurchaseCreated, status_code=201)
def buy_fuel(
    data: PurchaseCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.get(Product, data.product_id)
    if product is None:
        raise HTTPException(404, "Product not found.")
    if data.litres > product.available_litres:
        raise HTTPException(400, "Not enough fuel available.")

    total_price = (product.price_per_litre * data.litres).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    if total_price > user.account_balance:
        raise HTTPException(400, "Insufficient balance.")

    user.account_balance = func.round(User.account_balance - total_price, 2)
    product.available_litres = func.round(Product.available_litres - data.litres, 2)

    purchase = Purchase(
        user_id=user.id, product_id=product.id, litres=data.litres, total_price=total_price
    )
    db.add(purchase)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Insufficient balance or fuel. Please try again.")

    return PurchaseCreated(
        id=purchase.id,
        product=product.name,
        litres=purchase.litres,
        total_price=total_price,
        remaining_balance=user.account_balance,
        remaining_stock_litres=product.available_litres
    )


@router.get("/", response_model=list[PurchaseOut])
def get_purchases(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    purchases = (
        db.query(Purchase)
        .options(joinedload(Purchase.product))
        .filter(Purchase.user_id == user.id)
        .order_by(Purchase.created_at.desc())
        .all()
    )

    return [
        PurchaseOut(
            id=p.id,
            product=p.product.name,
            litres=p.litres,
            total_price=p.total_price,
            created_at=p.created_at.replace(tzinfo=timezone.utc),
        )
        for p in purchases
    ]