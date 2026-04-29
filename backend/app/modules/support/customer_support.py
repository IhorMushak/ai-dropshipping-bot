"""
Customer Support AI - автоматична відповідь клієнтам через Ollama
"""
import logging
import requests
from decimal import Decimal
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.database.models import Order, Customer

logger = logging.getLogger(__name__)


class CustomerSupport:
    """AI агент для підтримки клієнтів"""
    
    def __init__(self, ollama_url: str = "http://host.docker.internal:11434", model: str = "llama3"):
        self.ollama_url = ollama_url
        self.model = model
    
    def get_order_info(self, order_number: str, db: Session) -> Optional[Dict]:
        """Отримати інформацію про замовлення"""
        order = db.query(Order).filter(Order.order_number == order_number).first()
        if not order:
            return None
        
        return {
            "order_number": order.order_number,
            "status": order.status,
            "tracking_number": order.tracking_number,
            "carrier": order.carrier,
            "total_amount": order.total_amount,
            "order_placed_at": order.order_placed_at,
            "shipped_at": order.shipped_at,
            "delivered_at": order.delivered_at
        }
    
    def generate_response(self, user_message: str, context: str = None) -> str:
        """Генерує відповідь через Ollama"""
        prompt = f"""You are a customer support agent for an online dropshipping store called "AI Dropshipping Bot".
Be helpful, friendly, and professional.

Customer question: {user_message}

{context if context else ""}

Respond in a helpful manner. Keep response short and clear (max 100 words)."""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "max_tokens": 200}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', self._fallback_response())
            else:
                return self._fallback_response()
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return self._fallback_response()
    
    def _fallback_response(self) -> str:
        """Запасна відповідь якщо Ollama не доступна"""
        return "Thank you for contacting us! Please provide your order number and we'll check the status for you."
    
    def handle_inquiry(self, user_message: str, order_number: str = None, db: Session = None) -> Dict:
        """Обробляє запит клієнта"""
        
        context = ""
        
        if order_number and db:
            order_info = self.get_order_info(order_number, db)
            if order_info:
                context = f"\nOrder information:\n"
                context += f"- Status: {order_info['status']}\n"
                if order_info['tracking_number']:
                    context += f"- Tracking: {order_info['tracking_number']} ({order_info['carrier']})\n"
                if order_info['delivered_at']:
                    context += f"- Delivered on: {order_info['delivered_at']}\n"
                elif order_info['shipped_at']:
                    context += f"- Shipped on: {order_info['shipped_at']}\n"
        
        response = self.generate_response(user_message, context)
        inquiry_type = self._detect_inquiry_type(user_message)
        
        return {
            "user_message": user_message,
            "response": response,
            "inquiry_type": inquiry_type,
            "order_number": order_number,
            "context_used": bool(context)
        }
    
    def _detect_inquiry_type(self, message: str) -> str:
        """Визначає тип запиту"""
        message_lower = message.lower()
        
        if "order" in message_lower or "tracking" in message_lower or "shipping" in message_lower:
            return "order_status"
        elif "return" in message_lower or "refund" in message_lower:
            return "return_refund"
        elif "product" in message_lower or "quality" in message_lower:
            return "product_inquiry"
        elif "delivery" in message_lower or "shipping" in message_lower:
            return "shipping"
        else:
            return "general"
    
    def auto_refund(self, order_number: str, reason: str, db: Session) -> Dict:
        """Автоматичне повернення коштів (до 15% від вартості)"""
        order = db.query(Order).filter(Order.order_number == order_number).first()
        
        if not order:
            return {"error": "Order not found"}
        
        max_refund_percent = 15
        refund_amount = float(Decimal(str(order.total_amount)) * (max_refund_percent / 100))
        
        order.refund_amount = refund_amount
        order.refund_reason = reason
        order.status = "refunded"
        order.refunded_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"💰 Auto-refund ${refund_amount:.2f} for order {order_number}")
        
        return {
            "success": True,
            "order_number": order_number,
            "refund_amount": refund_amount,
            "refund_percent": max_refund_percent,
            "reason": reason
        }
