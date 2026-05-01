"""
Ad Campaign Creator - інтеграція з InfluenceFlow (безкоштовно)
"""
import logging
import uuid
from typing import Dict, List
from sqlalchemy.orm import Session
from app.database.models import Product, Campaign
from app.modules.influence import InfluenceFlowAPI

logger = logging.getLogger(__name__)


class CampaignCreator:
    def __init__(self):
        self.influence = InfluenceFlowAPI()
        self.default_budget = 500.0  # бюджет для інфлюенс-кампанії
    
    def create_campaign(self, product: Product, db: Session, platform: str = "influenceflow") -> Dict:
        logger.info(f"📢 Creating {platform} campaign for: {product.name}")
        
        # Генерація креативів
        headline, primary_text = self._generate_ad_copy(product)
        daily_budget = self._calculate_budget(product)
        
        # Створення кампанії в InfluenceFlow API
        influence_result = self.influence.create_influence_campaign(
            product=product,
            budget=daily_budget * 10,  # 10-денний бюджет
            influencers_needed=3
        )
        
        # Пошук інфлюенсерів для цього продукту
        influencers = self.influence.search_influencers(
            niche=product.category,
            limit=5
        )
        
        # Збереження в БД
        campaign = Campaign(
            id=str(uuid.uuid4()),
            product_id=product.id,
            platform=platform,
            headline=headline,
            primary_text=primary_text,
            daily_budget=daily_budget,
            status="active",
            target_audience=self._get_target_audience(product.category),
            creative_type="image",
            extra_data={
                "influence_campaign_id": influence_result.get("campaign_id"),
                "influencers_found": len(influencers),
                "mode": influence_result.get("mode", "real")
            }
        )
        
        db.add(campaign)
        db.commit()
        
        logger.info(f"✅ Campaign created: {campaign.id}")
        
        return {
            "success": True,
            "campaign_id": campaign.id,
            "product_id": product.id,
            "product_name": product.name,
            "platform": platform,
            "daily_budget": daily_budget,
            "headline": headline,
            "influence_campaign": influence_result,
            "influencers": influencers[:3],
            "status": "active"
        }
    
    def create_batch_campaigns(self, products: List[Product], db: Session, platform: str = "influenceflow") -> List[Dict]:
        results = []
        for product in products:
            result = self.create_campaign(product, db, platform)
            results.append(result)
        return results
    
    def _generate_ad_copy(self, product: Product) -> tuple:
        import random
        headlines = [f"🔥 {product.name[:50]}", f"✨ Best Deal on {product.name[:40]}", f"🚀 Limited Time: {product.name[:45]}"]
        texts = [f"Don't miss out! Free shipping. Order now!", f"Thousands of happy customers! Get {product.name[:30]} today!"]
        return random.choice(headlines), random.choice(texts)
    
    def _calculate_budget(self, product: Product) -> float:
        base_budget = 20.0
        if product.final_score:
            if product.final_score >= 85:
                return base_budget * 1.5
            elif product.final_score >= 70:
                return base_budget
        return base_budget
    
    def _get_target_audience(self, category: str = None) -> Dict:
        audiences = {
            "electronics": {"age_range": {"min": 18, "max": 45}, "interests": ["technology", "gadgets"]},
            "beauty": {"age_range": {"min": 18, "max": 40}, "interests": ["beauty", "skincare"]},
            "fashion": {"age_range": {"min": 16, "max": 35}, "interests": ["fashion", "clothing"]},
            "sports": {"age_range": {"min": 18, "max": 50}, "interests": ["fitness", "workout"]},
        }
        return audiences.get(category, {"age_range": {"min": 18, "max": 45}, "interests": ["shopping"]})
