"""
Medium Publisher - SEO паразит через Medium
"""
import logging
import requests
from typing import Dict
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database.models import Product

logger = logging.getLogger(__name__)


class MediumPublisher:
    def __init__(self):
        self.token = settings.MEDIUM_TOKEN
        self.has_credentials = bool(self.token)
    
    def generate_article(self, product: Product) -> str:
        """Генерує SEO-статтю з посиланням на продукт"""
        
        landing_url = f"http://localhost:8000/static/landings/{product.shopify_handle}.html" if product.shopify_handle else "#"
        
        templates = [
            f"""# Top 10 Trending Products You Must Know in 2026

## {product.name}

Looking for the best [product category]? We've found something amazing!

✨ Why this product is trending:
- High quality materials
- Affordable price
- Fast shipping worldwide

👉 **[Get yours here]({landing_url})**

Let me know in the comments if you have questions!

#trending #productreview #{product.category.replace(' ', '')}""",
            
            f"""# The Ultimate Guide to {product.name.split()[0]} in 2026

After testing dozens of products, here's what actually works:

**The winner:** {product.name}

What makes it special:
✓ Durable construction
✓ Great value for money  
✓ Positive customer reviews

**[Check current price →]({landing_url})**

What's your experience with {product.name.split()[0]}? Comment below!

#{product.category} #{product.name.split()[0].lower()} #amazonfinds""",
            
            f"""# 5 {product.category.title()} Products That Changed My Life

**Number 3 will surprise you!**

I've been testing {product.category} products for 3 months, and here's my honest review:

**{product.name}** - ⭐⭐⭐⭐ (4.5/5)
- Price: ${product.selling_price}
- Quality: Excellent
- Shipping: Fast

**[Read full review →]({landing_url})**

Would you try this? Let me know! #productreview #{product.category}"""
        ]
        
        import random
        return random.choice(templates)
    
    def publish(self, product: Product, db: Session) -> Dict:
        """Публікує статтю на Medium (або генерує для ручної публікації)"""
        
        article = self.generate_article(product)
        
        if not self.has_credentials:
            logger.info("📝 [MEDIUM] Article ready (simulation)")
            return {
                "success": True,
                "product_id": product.id,
                "platform": "medium",
                "mode": "simulation",
                "article": article,
                "message": "Copy this text to Medium"
            }
        
        # Реальна публікація через Medium API
        try:
            response = requests.post(
                "https://api.medium.com/v1/users/me/posts",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "title": f"Top {product.category.title()} Product for 2026",
                    "contentFormat": "markdown",
                    "content": article,
                    "tags": [product.category, "trending", "review"],
                    "publishStatus": "draft"
                },
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                return {
                    "success": True,
                    "product_id": product.id,
                    "platform": "medium",
                    "url": data['data']['url'],
                    "mode": "real"
                }
        except Exception as e:
            logger.error(f"Medium error: {e}")
        
        return {"success": False, "error": "Medium publish failed"}
