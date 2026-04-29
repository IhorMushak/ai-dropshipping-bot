"""
Ad Campaign Creator - симуляція створення рекламних кампаній
"""
import logging
from typing import Dict, List
from sqlalchemy.orm import Session
from app.database.models import Product, Campaign
import uuid

logger = logging.getLogger(__name__)


class CampaignCreator:
    """Створює рекламні кампанії для продуктів"""
    
    def __init__(self):
        self.platforms = ["meta", "tiktok", "google"]
        self.default_budget = 20.0
        self.target_roas = 2.5
    
    def create_campaign(self, product: Product, db: Session, platform: str = "meta") -> Dict:
        """Створити рекламну кампанію для продукту"""
        
        logger.info(f"📢 Creating {platform} campaign for: {product.name}")
        
        # Генеруємо рекламний текст
        headline, primary_text = self._generate_ad_copy(product)
        
        # Визначаємо бюджет на основі скору продукту
        daily_budget = self._calculate_budget(product)
        
        # Створюємо запис в БД згідно з моделлю Campaign
        campaign = Campaign(
            id=str(uuid.uuid4()),
            product_id=product.id,
            platform=platform,
            headline=headline,
            primary_text=primary_text,
            daily_budget=daily_budget,
            status="active",
            target_audience=self._get_target_audience(product.category),
            creative_type="image"
        )
        
        db.add(campaign)
        db.commit()
        
        logger.info(f"✅ Campaign created: {campaign.id} | Budget: ${daily_budget}/day")
        
        return {
            "success": True,
            "campaign_id": campaign.id,
            "product_id": product.id,
            "product_name": product.name,
            "platform": platform,
            "daily_budget": daily_budget,
            "headline": headline,
            "primary_text": primary_text[:100] + "..." if len(primary_text) > 100 else primary_text,
            "status": "active"
        }
    
    def create_batch_campaigns(self, products: List[Product], db: Session, platform: str = "meta") -> List[Dict]:
        """Створити кампанії для кількох продуктів"""
        
        results = []
        for product in products:
            result = self.create_campaign(product, db, platform)
            results.append(result)
        
        logger.info(f"📢 Created {len(results)} campaigns")
        return results
    
    def _generate_ad_copy(self, product: Product) -> tuple:
        """Генерує заголовок та текст реклами"""
        import random
        
        headlines = [
            f"🔥 {product.name[:50]}",
            f"✨ Best Deal on {product.name[:40]}",
            f"🚀 Limited Time: {product.name[:45]}",
            f"💎 Customer Favorite: {product.name[:40]}"
        ]
        
        texts = [
            f"Don't miss out on this amazing deal! Free shipping on all orders. Order now before they're gone!",
            f"Thousands of happy customers! Get {product.name[:30]} today with 30% discount. Limited stock available!",
            f"Trending product! Join thousands of satisfied customers. Special offer ends soon. Shop now!",
            f"Premium quality {product.category or 'product'} at unbeatable price. Fast shipping, 24/7 support. Order today!"
        ]
        
        return random.choice(headlines), random.choice(texts)
    
    def _calculate_budget(self, product: Product) -> float:
        """Розраховує денний бюджет на основі скору продукту"""
        base_budget = self.default_budget
        
        if product.final_score:
            if product.final_score >= 85:
                return base_budget * 1.5
            elif product.final_score >= 70:
                return base_budget
            else:
                return base_budget * 0.5
        
        return base_budget
    
    def _get_target_audience(self, category: str = None) -> Dict:
        """Визначає цільову аудиторію"""
        audiences = {
            "electronics": {"age_range": {"min": 18, "max": 45}, "interests": ["technology", "gadgets"]},
            "beauty": {"age_range": {"min": 18, "max": 40}, "interests": ["beauty", "skincare"]},
            "fashion": {"age_range": {"min": 16, "max": 35}, "interests": ["fashion", "clothing"]},
            "sports": {"age_range": {"min": 18, "max": 50}, "interests": ["fitness", "workout"]},
            "home": {"age_range": {"min": 25, "max": 55}, "interests": ["home decor"]},
            "pet": {"age_range": {"min": 22, "max": 50}, "interests": ["pets", "dogs", "cats"]},
        }
        return audiences.get(category, {"age_range": {"min": 18, "max": 45}, "interests": ["shopping"]})
