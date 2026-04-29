"""
Payment API endpoints - PayPal integration
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Product
from app.modules.payment import PayPalPayment

router = APIRouter()
payment = PayPalPayment()


@router.post("/payment/create/{product_id}")
async def create_payment(
    product_id: str,
    success_url: str = "http://localhost:3000/success",
    cancel_url: str = "http://localhost:3000/cancel",
    db: Session = Depends(get_db)
):
    """Створює PayPal замовлення та повертає URL для оплати"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    result = payment.create_order(product, success_url, cancel_url)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail="Failed to create payment")
    
    return result


@router.post("/payment/capture/{paypal_order_id}")
async def capture_payment(paypal_order_id: str):
    """Захоплює оплату після підтвердження"""
    result = payment.capture_order(paypal_order_id)
    return result


@router.get("/payment/success")
async def payment_success(request: Request):
    """Callback після успішної оплати"""
    token = request.query_params.get("token")
    payer_id = request.query_params.get("PayerID")
    
    if token:
        result = payment.capture_order(token)
        if result.get("success"):
            return {"message": "Payment successful!", "order_id": token}
    
    return {"message": "Payment Successful", "token": token}
