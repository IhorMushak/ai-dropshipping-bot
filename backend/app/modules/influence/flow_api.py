"""
InfluenceFlow API Integration - 100% безкоштовний вплив-маркетинг
Документація: https://influenceflow.io/resources/influenceflow-developer-documentation-api-reference
"""
import logging
import requests
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database.models import Product, Campaign

logger = logging.getLogger(__name__)


class InfluenceFlowAPI:
    """Інтеграція з InfluenceFlow - безкоштовна платформа для інфлюенс-маркетингу"""
    
    def __init__(self):
        self.api_key = settings.INFLUENCEFLOW_API_KEY
        self.base_url = settings.INFLUENCEFLOW_API_URL
        self.has_credentials = bool(self.api_key)
        
        if not self.has_credentials:
            logger.warning("⚠️ InfluenceFlow API key missing. Get free key from influenceflow.io")
        else:
            logger.info("✅ InfluenceFlow API initialized")
    
    def get_headers(self) -> Dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def search_influencers(self, niche: str = None, min_followers: int = 10000, max_followers: int = 100000, limit: int = 20) -> List[Dict]:
        """Пошук інфлюенсерів за нішею [citation:6]"""
        if not self.has_credentials:
            return self._mock_influencers(niche, limit)
        
        try:
            params = {
                "limit": limit,
                "min_followers": min_followers,
                "max_followers": max_followers
            }
            if niche:
                params["niche"] = niche
            
            response = requests.get(
                f"{self.base_url}/creators",
                headers=self.get_headers(),
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                creators = data.get('creators', data.get('items', []))
                logger.info(f"Found {len(creators)} influencers for niche: {niche}")
                return creators
            else:
                logger.error(f"InfluenceFlow error: {response.status_code}")
                return self._mock_influencers(niche, limit)
        except Exception as e:
            logger.error(f"InfluenceFlow API error: {e}")
            return self._mock_influencers(niche, limit)
    
    def create_influence_campaign(self, product: Product, budget: float = 500, influencers_needed: int = 5) -> Dict:
        """Створення маркетингової кампанії через InfluenceFlow [citation:5]"""
        if not self.has_credentials:
            return self._mock_campaign(product, budget, influencers_needed)
        
        try:
            campaign_data = {
                "name": f"AI Campaign: {product.name[:50]}",
                "budget": budget,
                "influencers_needed": influencers_needed,
                "description": product.generated_description or f"Promote {product.name}",
                "product_url": f"http://localhost:8000/static/landings/{product.shopify_handle}.html" if product.shopify_handle else None,
                "target_audience": {
                    "interests": [product.category] if product.category else [],
                    "age_range": {"min": 18, "max": 45}
                }
            }
            
            response = requests.post(
                f"{self.base_url}/campaigns",
                headers=self.get_headers(),
                json=campaign_data,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                logger.info(f"✅ Influence campaign created: {data.get('id')}")
                return {
                    "success": True,
                    "campaign_id": data.get('id'),
                    "platform": "influenceflow",
                    "budget": budget,
                    "influencers_needed": influencers_needed,
                    "status": data.get('status', 'active')
                }
            else:
                logger.error(f"Campaign creation failed: {response.status_code}")
                return self._mock_campaign(product, budget, influencers_needed)
        except Exception as e:
            logger.error(f"InfluenceFlow campaign error: {e}")
            return self._mock_campaign(product, budget, influencers_needed)
    
    def get_campaign_status(self, campaign_id: str) -> Optional[Dict]:
        """Отримання статусу кампанії"""
        if not self.has_credentials:
            return {"status": "active", "applications": 3}
        
        try:
            response = requests.get(
                f"{self.base_url}/campaigns/{campaign_id}",
                headers=self.get_headers(),
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting campaign status: {e}")
        return None
    
    def process_payment(self, campaign_id: str, amount: float, creator_id: str) -> Dict:
        """Обробка платежу через InfluenceFlow (Stripe/PayPal) [citation:5]"""
        if not self.has_credentials:
            return {"success": True, "status": "simulated", "amount": amount}
        
        try:
            payment_data = {
                "campaign_id": campaign_id,
                "creator_id": creator_id,
                "amount": amount,
                "currency": "USD"
            }
            response = requests.post(
                f"{self.base_url}/payments",
                headers=self.get_headers(),
                json=payment_data,
                timeout=30
            )
            if response.status_code == 201:
                return {"success": True, "status": "processed", "amount": amount}
        except Exception as e:
            logger.error(f"Payment error: {e}")
        return {"success": False, "error": "Payment failed"}
    
    def _mock_influencers(self, niche: str, limit: int) -> List[Dict]:
        """Mock-дані для тестування"""
        mock = [
            {
                "id": f"inf_{i}",
                "name": f"Influencer {i}",
                "niche": niche or "general",
                "followers": 25000 + i * 5000,
                "engagement_rate": 3.5 + i * 0.2,
                "platform": "instagram",
                "price_per_post": 150 + i * 25
            } for i in range(min(limit, 10))
        ]
        return mock
    
    def _mock_campaign(self, product: Product, budget: float, influencers_needed: int) -> Dict:
        """Mock-дані для кампанії"""
        return {
            "success": True,
            "campaign_id": f"mock_{product.id[:8]}",
            "platform": "influenceflow",
            "budget": budget,
            "influencers_needed": influencers_needed,
            "status": "active",
            "mode": "simulation"
        }
