"""
Main Trend Scanner - orchestrates all sources with auto product creation
"""
import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import requests

from app.database.session import SessionLocal
from app.database.models import Trend, Product
from app.modules.trend_scanner.sources.google import GoogleTrendsSource
from app.modules.trend_scanner.sources.tiktok import TikTokTrendsSource

logger = logging.getLogger(__name__)


class TrendScanner:
    def __init__(self):
        self.sources = {
            'google': GoogleTrendsSource(),
            'tiktok': TikTokTrendsSource(),
        }
        self.min_score_for_product = 80
        self.auto_create_products = True
    
    def scan_all(self, geo: str = 'US') -> Dict[str, List[Dict]]:
        results = {}
        for source_name, source in self.sources.items():
            try:
                if source_name == 'google':
                    trends = source.get_trending_searches(geo=geo)
                else:
                    trends = source.get_trending_hashtags()
                results[source_name] = trends
                logger.info(f"Scanned {len(trends)} trends from {source_name}")
            except Exception as e:
                logger.error(f"Failed to scan {source_name}: {e}")
                results[source_name] = []
        return results
    
    def _search_product_image(self, keyword: str) -> str:
        """Пошук зображення товару через AliExpress API"""
        try:
            from app.modules.supplier.dual import DualSupplier
            supplier = DualSupplier()
            results = supplier.search_all(keyword, limit=1)
            
            if results.get('aliexpress') and results['aliexpress']:
                image_url = results['aliexpress'][0].get('image_url')
                if image_url:
                    return image_url
            
            # Fallback: зображення за замовчуванням
            return f"https://placehold.co/400x300/1a1a2e/3b82f6?text={keyword.replace(' ', '+')}"
        except Exception as e:
            logger.error(f"Failed to get image for {keyword}: {e}")
            return f"https://placehold.co/400x300/1a1a2e/3b82f6?text={keyword.replace(' ', '+')}"
    
    def _create_product_from_trend(self, trend: Trend, db: Session) -> Product:
        """Створює продукт з тренду (з зображенням)"""
        
        product_name = f"{trend.keyword.title()} - Premium Quality"
        description = self._generate_description(trend.keyword, trend.category)
        
        # Отримуємо зображення
        image_url = self._search_product_image(trend.keyword)
        
        supplier_cost = self._estimate_supplier_cost(trend.category)
        selling_price = supplier_cost * 2.5
        shipping_cost = 3.99
        
        product = Product(
            id=str(uuid.uuid4()),
            name=product_name,
            description=description,
            category=trend.category,
            status='discovered',
            trend_score=float(trend.score),
            supplier_cost=supplier_cost,
            selling_price=selling_price,
            shipping_cost=shipping_cost,
            total_cost=supplier_cost + shipping_cost,
            margin_percent=((selling_price - (supplier_cost + shipping_cost)) / selling_price) * 100,
            discovered_at=datetime.utcnow(),
            tags=[trend.keyword, trend.category],
            images=[image_url] if image_url else [],
            extra_data={
                'source_trend_id': trend.id,
                'source_trend_keyword': trend.keyword,
                'auto_created': True
            }
        )
        
        db.add(product)
        db.flush()
        logger.info(f"✅ Created product: {product_name} with image: {image_url[:50]}...")
        return product
    
    def save_to_db(self, trends_data: Dict[str, List[Dict]], db: Session) -> tuple:
        """Зберігає тренди та створює продукти"""
        saved_count = 0
        created_products = []
        
        for source, trends in trends_data.items():
            for trend_data in trends:
                existing = db.query(Trend).filter(Trend.keyword == trend_data['keyword']).first()
                if not existing:
                    trend = Trend(
                        keyword=trend_data['keyword'],
                        source=trend_data['source'],
                        score=trend_data.get('score', 50.0),
                        category=trend_data.get('category', 'general'),
                        raw_data=trend_data.get('raw_data', {})
                    )
                    db.add(trend)
                    db.flush()
                    saved_count += 1
                    
                    if self.auto_create_products and trend.score >= self.min_score_for_product:
                        product = self._create_product_from_trend(trend, db)
                        created_products.append({
                            'trend_keyword': trend.keyword,
                            'product_id': product.id,
                            'product_name': product.name,
                            'trend_score': trend.score,
                            'image': product.images[0] if product.images else None
                        })
                        logger.info(f"Auto-created product from trend: {trend.keyword} (score: {trend.score})")
        
        db.commit()
        return saved_count, created_products
    
    def _generate_description(self, keyword: str, category: str) -> str:
        descriptions = {
            'electronics': f"High-quality {keyword}. Perfect for everyday use. Features advanced technology and durable design. Satisfaction guaranteed.",
            'beauty': f"Premium {keyword} for your beauty routine. Made with natural ingredients. Visible results in days.",
            'home': f"Transform your space with this {keyword}. Stylish, functional, and built to last. Customer favorite!",
            'fashion': f"Trendy {keyword} that elevates your style. Comfortable fit, premium materials. Shop now!",
            'sports': f"Professional {keyword} for fitness enthusiasts. Durable, reliable, and performance-focused.",
            'pet': f"Spoil your furry friend with this {keyword}. Safe, fun, and loved by pets everywhere.",
            'baby': f"Safe and gentle {keyword} for your little one. Parent-approved, baby-loved.",
            'general': f"Amazing {keyword} that exceeds expectations. Order now and see the difference!"
        }
        return descriptions.get(category, descriptions['general'])
    
    def _estimate_supplier_cost(self, category: str) -> float:
        costs = {
            'electronics': 12.99, 'beauty': 8.99, 'home': 10.99,
            'fashion': 7.99, 'sports': 9.99, 'pet': 6.99, 'baby': 8.49, 'general': 9.99
        }
        return costs.get(category, 9.99)
    
    def scan_and_save(self, geo: str = 'US') -> Dict:
        db = SessionLocal()
        try:
            trends = self.scan_all(geo=geo)
            saved, created_products = self.save_to_db(trends, db)
            return {
                'scanned': {'google': len(trends.get('google', [])), 'tiktok': len(trends.get('tiktok', []))},
                'total_scanned': sum(len(trends.get(k, [])) for k in trends),
                'new_trends_saved': saved,
                'products_created': len(created_products),
                'created_products': created_products,
                'min_score_threshold': self.min_score_for_product,
                'timestamp': datetime.utcnow().isoformat()
            }
        finally:
            db.close()
