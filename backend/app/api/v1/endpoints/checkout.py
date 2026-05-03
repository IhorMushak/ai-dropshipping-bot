"""
Checkout API - створення замовлення ДО оплати
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Product, Order
import uuid
from datetime import datetime

router = APIRouter()


class CheckoutRequest(BaseModel):
    product_id: str
    name: str
    email: EmailStr
    phone: str = None
    address_line1: str
    address_line2: str = None
    city: str
    state: str = None
    zip: str
    country: str = "US"


class CheckoutResponse(BaseModel):
    success: bool
    checkout_id: str
    order_number: str
    product_name: str
    amount: float
    paypal_url: str


@router.post("/checkout/create", response_model=CheckoutResponse)
async def create_checkout(
    data: CheckoutRequest,
    db: Session = Depends(get_db)
):
    """Створює замовлення та повертає посилання на PayPal"""
    
    # Знаходимо продукт
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Створюємо замовлення
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    order = Order(
        id=str(uuid.uuid4()),
        order_number=order_number,
        marketplace="checkout",
        product_id=product.id,
        customer_name=data.name,
        customer_email=data.email,
        customer_phone=data.phone,
        shipping_name=data.name,
        shipping_email=data.email,
        shipping_phone=data.phone,
        shipping_address_line1=data.address_line1,
        shipping_address_line2=data.address_line2,
        shipping_city=data.city,
        shipping_state=data.state,
        shipping_zip=data.zip,
        shipping_country=data.country,
        items=[{
            "product_id": product.id,
            "name": product.name,
            "quantity": 1,
            "price": float(product.selling_price or 29.99)
        }],
        subtotal=float(product.selling_price or 29.99),
        total_amount=float(product.selling_price or 29.99),
        status="checkout_created",
        checkout_status="address_collected",
        order_placed_at=datetime.utcnow()
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Створюємо PayPal замовлення
    from app.modules.payment.paypal import PayPalPayment
    paypal = PayPalPayment()
    
    paypal_result = paypal.create_order(
        product=product,
        custom_id=order.id,
        success_url="https://ihormushak.github.io/ai-dropshipping-bot/success.html",
        cancel_url="https://ihormushak.github.io/ai-dropshipping-bot/cancel.html"
    )
    
    if paypal_result.get("success"):
        order.paypal_order_id = paypal_result.get("order_id")
        order.checkout_status = "payment_pending"
        db.commit()
        
        return CheckoutResponse(
            success=True,
            checkout_id=order.id,
            order_number=order_number,
            product_name=product.name,
            amount=float(product.selling_price or 29.99),
            paypal_url=paypal_result.get("approval_url")
        )
    else:
        order.status = "checkout_failed"
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to create PayPal order")
