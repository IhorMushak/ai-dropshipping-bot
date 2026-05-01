"""
Medium Publisher - SEO паразит через Medium
"""
import logging
import random
from typing import Dict
from sqlalchemy.orm import Session
from app.database.models import Product

logger = logging.getLogger(__name__)


class MediumPublisher:
    """Генерація та публікація статей на Medium"""
    
    def __init__(self):
        self.templates = {
            "top10": "Top 10 {category} Products You Need in 2026",
            "best": "Best {category} for {problem} - Ultimate Guide",
            "review": "{product_name} Review: Is It Worth Your Money?",
            "comparison": "5 Best {category} Compared: Which One to Choose?",
            "howto": "How to Choose the Best {category} - Complete Guide"
        }
        
        self.problems = {
            "electronics": ["tech enthusiasts", "gadget lovers", "remote workers"],
            "beauty": ["skincare routine", "self-care", "beauty lovers"],
            "home": ["home organization", "decluttering", "home improvement"],
            "sports": ["fitness journey", "workout routine", "active lifestyle"],
            "fashion": ["wardrobe upgrade", "style inspiration", "trendy outfits"],
            "pet": ["pet care", "furry friends", "pet parents"],
            "baby": ["new parents", "baby essentials", "parenthood journey"]
        }
    
    def generate_article(self, product: Product) -> Dict:
        """Генерує SEO-оптимізовану статтю"""
        
        landing_url = f"http://localhost:8000/static/landings/{product.shopify_handle}.html" if product.shopify_handle else "#"
        category = product.category or "product"
        problem_list = self.problems.get(category, ["shoppers", "enthusiasts"])
        
        titles = [
            f"Top 10 {category.title()} Products You Must Know in 2026",
            f"Best {category.title()} for {random.choice(problem_list)} - Expert Review",
            f"{product.name[:50]} - The Ultimate {category.title()} for 2026",
            f"5 {category.title()} That Will Change Your Life (Number 3 is {product.name[:30]})",
            f"Complete Guide to {category.title()} - Why {product.name[:30]} is #1"
        ]
        
        article = f"""# {random.choice(titles)}

## Why {category.title()} Matters in 2026

The {category} market has exploded with amazing options. After testing dozens of products, we've found something truly special.

## Our Top Pick: {product.name}

![{product.name}]({product.images[0] if product.images else ''})

✨ **Key Features:**
- Premium quality materials
- Affordable pricing
- Fast shipping worldwide

> "{product.generated_description or 'This product exceeded all expectations. Highly recommended!'}"

## Where to Buy

Ready to try {product.name}? Click the link below for the best price:

👉 **[Check Current Price on {category.title()} →]({landing_url})**

## Final Verdict

After extensive testing, {product.name} stands out as the best {category} product in its class. Highly recommended!

*Have you tried this product? Share your experience in the comments!*

#productreview #{category.lower()} #{product.name.lower().replace(' ', '')[:20]} #2026 #amazonfinds
"""
        
        return {
            "title": random.choice(titles),
            "content": article,
            "tags": [category.lower(), "review", "trending", "2026"],
            "url": landing_url
        }
    
    def publish(self, product: Product, db: Session) -> Dict:
        """Готує статтю для публікації (симуляція)"""
        
        article = self.generate_article(product)
        
        # Зберігаємо статтю в файл для ручної публікації
        import os
        os.makedirs("/tmp/seo_articles", exist_ok=True)
        filename = f"/tmp/seo_articles/medium_{product.id[:8]}.md"
        with open(filename, "w") as f:
            f.write(f"# {article['title']}\n\n{article['content']}")
        
        logger.info(f"📝 Medium article generated: {filename}")
        
        return {
            "success": True,
            "product_id": product.id,
            "platform": "medium",
            "title": article['title'],
            "article_preview": article['content'][:300] + "...",
            "download_url": filename,
            "instructions": "Copy this article to Medium.com for publishing"
        }
