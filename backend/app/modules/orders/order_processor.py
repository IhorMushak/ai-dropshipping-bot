"""
Order Processor - автоматичне виконання замовлень
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database.models import Order, Product, Customer

logger = logging.getLogger(__name__)


class OrderProcessor:
    """Автоматична обробка замовлень"""
    
    def create_order(self, db: Session, order_data: Dict) -> Dict:
        """Створити нове замовлення"""
        
        product = db.query(Product).filter(
            Product.id == order_data.get('product_id')
        ).first()
        
        if not product:
            return {"error": "Product not found"}
        
        customer = self._get_or_create_customer(db, order_data)
        
        quantity = order_data.get('quantity', 1)
        subtotal = Decimal(str(product.selling_price or 29.99)) * quantity
        shipping_charged = Decimal(str(order_data.get('shipping_charged', 5.99)))
        total_amount = subtotal + shipping_charged
        
        product_cost = Decimal(str(product.supplier_cost or 9.99)) * quantity
        shipping_cost = Decimal(str(order_data.get('shipping_cost', 3.99)))
        marketplace_fee = Decimal('2.0')
        total_cost = product_cost + shipping_cost + marketplace_fee
        profit = total_amount - total_cost
        
        order = Order(
            id=str(uuid.uuid4()),
            order_number=f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            marketplace=order_data.get('marketplace', 'shopify'),
            product_id=product.id,
            customer_id=customer.id if customer else None,
            customer_name=order_data.get('customer_name'),
            customer_email=order_data.get('customer_email'),
            shipping_address=order_data.get('shipping_address', {}),
            items=[{"product_id": product.id, "name": product.name, "quantity": quantity, "price": float(product.selling_price or 29.99)}],
            subtotal=float(subtotal),
            shipping_charged=float(shipping_charged),
            total_amount=float(total_amount),
            product_cost=float(product_cost),
            shipping_cost=float(shipping_cost),
            marketplace_fee=float(marketplace_fee),
            total_cost=float(total_cost),
            profit=float(profit),
            status="pending",
            payment_status="paid",
            fulfillment_status="unfulfilled",
            order_placed_at=datetime.utcnow()
        )
        
        db.add(order)
        
        # Оновлюємо метрики продукту
        product.total_sales = (product.total_sales or 0) + quantity
        product.total_revenue = float(Decimal(str(product.total_revenue or 0)) + total_amount)
        product.total_profit = float(Decimal(str(product.total_profit or 0)) + profit)
        
        if customer:
            customer.total_orders = (customer.total_orders or 0) + 1
            customer.total_spent = float(Decimal(str(customer.total_spent or 0)) + total_amount)
            customer.last_order_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"✅ Order created: {order.order_number} | Amount: ${float(total_amount)} | Profit: ${float(profit):.2f}")
        
        return {
            "success": True,
            "order_id": order.id,
            "order_number": order.order_number,
            "total_amount": float(total_amount),
            "profit": float(profit),
            "status": order.status
        }
    
    def process_order(self, order_id: str, db: Session) -> Dict:
        """Обробити замовлення"""
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return {"error": "Order not found"}
        
        if order.status != "pending":
            return {"error": f"Order already {order.status}"}
        
        order.status = "confirmed"
        order.order_confirmed_at = datetime.utcnow()
        db.commit()
        
        supplier_order_id = f"SUP-{order.order_number}"
        order.supplier_order_id = supplier_order_id
        order.status = "processing"
        order.processing_started_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"📦 Order {order.order_number} sent to supplier")
        
        return {
            "success": True,
            "order_id": order.id,
            "order_number": order.order_number,
            "supplier_order_id": supplier_order_id,
            "status": order.status
        }
    
    def update_shipping(self, order_id: str, tracking_number: str, carrier: str, db: Session) -> Dict:
        """Оновити інформацію про доставку"""
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return {"error": "Order not found"}
        
        order.tracking_number = tracking_number
        order.carrier = carrier
        order.status = "shipped"
        order.shipped_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "order_id": order.id,
            "order_number": order.order_number,
            "tracking_number": tracking_number,
            "status": order.status
        }
    
    def confirm_delivery(self, order_id: str, db: Session) -> Dict:
        """Підтвердити доставку"""
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return {"error": "Order not found"}
        
        order.status = "delivered"
        order.delivered_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status
        }
    
    def get_order_status(self, order_id: str, db: Session) -> Dict:
        """Отримати статус замовлення"""
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return {"error": "Order not found"}
        
        return {
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "payment_status": order.payment_status,
            "fulfillment_status": order.fulfillment_status,
            "tracking_number": order.tracking_number,
            "order_placed_at": order.order_placed_at
        }
    
    def _get_or_create_customer(self, db: Session, order_data: Dict):
        """Знайти або створити клієнта"""
        email = order_data.get('customer_email')
        
        if not email:
            return None
        
        customer = db.query(Customer).filter(Customer.email == email).first()
        
        if not customer:
            customer = Customer(
                id=str(uuid.uuid4()),
                email=email,
                first_name=order_data.get('customer_first_name'),
                last_name=order_data.get('customer_last_name'),
                phone=order_data.get('customer_phone'),
                total_orders=0,
                total_spent=0.0,
                is_active=True
            )
            db.add(customer)
            db.flush()
        
        return customer
