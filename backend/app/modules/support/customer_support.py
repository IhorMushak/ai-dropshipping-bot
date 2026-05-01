"""
Customer Support AI - використовує Ollama для відповідей
"""
import logging
import requests
import json
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import Order

logger = logging.getLogger(__name__)


class CustomerSupport:
    """AI агент для підтримки клієнтів через Ollama"""
    
    def __init__(self):
        self.ollama_url = "http://ollama:11434"
        self.model = "llama3"
    
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
        
        system_prompt = """You are a professional customer support agent for an online dropshipping store called "AI Dropshipping Bot".
Be helpful, friendly, and professional. Keep responses short and clear (max 150 words).
If you don't know something, be honest and say you'll check."""
        
        user_prompt = f"Customer: {user_message}\n\n"
        if context:
            user_prompt += f"Order context: {context}\n\n"
        user_prompt += "Your response:"
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": user_prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "max_tokens": 300}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '')
                return result.strip()
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return self._fallback_response()
                
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return self._fallback_response()
    
    def _fallback_response(self) -> str:
        """Запасна відповідь"""
        return "Thank you for contacting us! Please provide your order number and we'll check the status for you."
    
    def handle_inquiry(self, user_message: str, order_number: str = None, db: Session = None) -> Dict:
        """Обробляє запит клієнта"""
        
        context = ""
        
        if order_number and db:
            order_info = self.get_order_info(order_number, db)
            if order_info:
                context = f"Order #{order_number}: status={order_info['status']}"
                if order_info['tracking_number']:
                    context += f", tracking={order_info['tracking_number']}"
                if order_info['delivered_at']:
                    context += f", delivered on {order_info['delivered_at']}"
                elif order_info['shipped_at']:
                    context += f", shipped on {order_info['shipped_at']}"
        
        response = self.generate_response(user_message, context)
        inquiry_type = self._detect_inquiry_type(user_message)
        
        return {
            "user_message": user_message,
            "response": response,
            "inquiry_type": inquiry_type,
            "order_number": order_number,
            "context_used": bool(context),
            "model": self.model
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
        elif "delivery" in message_lower:
            return "delivery"
        else:
            return "general"
    
    def auto_refund(self, order_number: str, reason: str, db: Session) -> Dict:
        """Автоматичне повернення коштів"""
        order = db.query(Order).filter(Order.order_number == order_number).first()
        
        if not order:
            return {"error": "Order not found"}
        
        # Перевіряємо чи можна повернути
        if order.status in ["shipped", "delivered"]:
            return {"error": "Order already shipped, cannot auto-refund"}
        
        refund_amount = order.total_amount
        order.status = "refunded"
        order.refunded_at = datetime.utcnow()
        order.refund_reason = reason
        db.commit()
        
        logger.info(f"💰 Auto-refund ${refund_amount:.2f} for order {order_number}")
        
        return {
            "success": True,
            "order_number": order_number,
            "refund_amount": refund_amount,
            "reason": reason
        }
