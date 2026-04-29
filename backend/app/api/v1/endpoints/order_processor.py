"""
Order Processor API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.modules.orders import OrderProcessor

router = APIRouter()
processor = OrderProcessor()


@router.post("/orders/create")
async def create_order(
    product_id: str,
    customer_name: str,
    customer_email: str,
    quantity: int = Query(1, ge=1, le=100),
    shipping_address: dict = None,
    marketplace: str = "shopify",
    db: Session = Depends(get_db)
):
    """Створити нове замовлення"""
    order_data = {
        "product_id": product_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "quantity": quantity,
        "shipping_address": shipping_address or {},
        "marketplace": marketplace
    }
    result = processor.create_order(db, order_data)
    return result


@router.post("/orders/{order_id}/process")
async def process_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Обробити замовлення (підтвердити, передати постачальнику)"""
    result = processor.process_order(order_id, db)
    return result


@router.post("/orders/{order_id}/ship")
async def update_shipping(
    order_id: str,
    tracking_number: str,
    carrier: str = "AliExpress Standard",
    db: Session = Depends(get_db)
):
    """Оновити інформацію про доставку"""
    result = processor.update_shipping(order_id, tracking_number, carrier, db)
    return result


@router.post("/orders/{order_id}/deliver")
async def confirm_delivery(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Підтвердити доставку"""
    result = processor.confirm_delivery(order_id, db)
    return result


@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    reason: str = "Customer request",
    db: Session = Depends(get_db)
):
    """Скасувати замовлення"""
    result = processor.cancel_order(order_id, reason, db)
    return result


@router.get("/orders/{order_id}/status")
async def get_order_status(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Отримати статус замовлення"""
    result = processor.get_order_status(order_id, db)
    return result
