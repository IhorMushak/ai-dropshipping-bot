"""
Customer Support API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.modules.support import CustomerSupport

router = APIRouter()
support = CustomerSupport()


@router.post("/support/chat")
async def chat(
    message: str,
    order_number: str = Query(None, description="Order number if available"),
    db: Session = Depends(get_db)
):
    """Чат з AI підтримкою"""
    result = support.handle_inquiry(message, order_number, db)
    return result


@router.post("/support/auto-refund")
async def auto_refund(
    order_number: str,
    reason: str = "Customer request",
    db: Session = Depends(get_db)
):
    """Автоматичне повернення коштів"""
    result = support.auto_refund(order_number, reason, db)
    return result


@router.get("/support/order-status/{order_number}")
async def get_order_status(
    order_number: str,
    db: Session = Depends(get_db)
):
    """Отримати статус замовлення для клієнта"""
    info = support.get_order_info(order_number, db)
    if not info:
        raise HTTPException(status_code=404, detail="Order not found")
    return info
