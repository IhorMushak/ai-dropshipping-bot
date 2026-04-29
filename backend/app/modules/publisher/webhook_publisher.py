"""
Webhook Publisher - симуляція публікації
"""
import logging
from sqlalchemy.sql import func
from app.database.models import Product

logger = logging.getLogger(__name__)


class WebhookPublisher:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
    
    def publish_product(self, product: Product, db) -> dict:
        """Публікує продукт"""
        
        logger.info(f"📦 Publishing product: {product.name}")
        
        # Оновлюємо статус
        product.status = "published"
        product.published_at = func.now()
        db.commit()
        
        return {
            "success": True,
            "product_id": product.id,
            "product_name": product.name,
            "status": "published"
        }
