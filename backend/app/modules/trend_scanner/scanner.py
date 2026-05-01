"""
Main Trend Scanner - orchestrates all sources with auto product creation
"""
import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.database.session import SessionLocal
from app.database.models import Trend, Product
from app.modules.trend_scanner.sources.google import GoogleTrendsSource
from app.modules.trend_scanner.sources.tiktok import TikTokTrendsSource

logger = logging.getLogger(__name__)


class TrendScanner:
    """Orchestrates trend scanning from multiple sources"""
    
    def __init__(self):
        self.sources = {
            'google': GoogleTrendsSource(),
            'tiktok': TikTokTrendsSource(),
        }
        self.min_score_for_product = 80  # Only create products from trends with score >= 80
        self.auto_create_products = True
    
    def scan_all(self, geo: str = 'US') -> Dict[str, List[Dict]]:
        """Scan trends from all sources"""
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
    
    def save_to_db(self, trends_data: Dict[str, List[Dict]], db: Session) -> int:
        """Save scanned trends to database and auto-create products for high-score trends"""
        saved_count = 0
        created_products = []
        
        for source, trends in trends_data.items():
            for trend_data in trends:
                # Check if trend already exists
                existing = db.query(Trend).filter(
                    Trend.keyword == trend_data['keyword']
                ).first()
                
                if not existing:
                    trend = Trend(
                        keyword=trend_data['keyword'],
                        source=trend_data['source'],
                        score=trend_data.get('score', 50.0),
                        category=trend_data.get('category', 'general'),
                        search_volume=trend_data.get('search_volume'),
                        competition=trend_data.get('competition'),
                        raw_data=trend_data.get('raw_data', {})
                    )
                    db.add(trend)
                    db.flush()
                    saved_count += 1
                    
                    # Auto-create product if score is high enough
                    if self.auto_create_products and trend.score >= self.min_score_for_product:
                        product = self._create_product_from_trend(trend, db)
                        created_products.append({
                            'trend_keyword': trend.keyword,
                            'product_id': product.id,
                            'product_name': product.name,
                            'trend_score': trend.score
                        })
                        logger.info(f"Auto-created product from trend: {trend.keyword} (score: {trend.score})")
        
        db.commit()
        
        logger.info(f"Saved {saved_count} new trends, created {len(created_products)} products")
        return saved_count, created_products
    
    def _create_product_from_trend(self, trend: Trend, db: Session) -> Product:
        """Create a product from a trend"""
        
        # Generate product name from trend keyword
        product_name = self._generate_product_name(trend.keyword)
        
        # Generate description
        description = self._generate_description(trend.keyword, trend.category)
        
        # Calculate estimated prices
        supplier_cost = self._estimate_supplier_cost(trend.category)
        selling_price = supplier_cost * 2.5  # 150% markup
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
            extra_data={
                'source_trend_id': trend.id,
                'source_trend_keyword': trend.keyword,
                'auto_created': True
            }
        )
        
        db.add(product)
        db.flush()
        
        return product
    
    def _generate_product_name(self, keyword: str) -> str:
        """Generate a product name from a trend keyword"""
        # Capitalize and make it product-ready
        words = keyword.split()
        if len(words) <= 3:
            return ' '.join(words).title() + " - Premium Quality"
        else:
            return ' '.join(words[:3]).title() + " - Best Seller"
    
    def _generate_description(self, keyword: str, category: str) -> str:
        """Generate a product description"""
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
        """Estimate supplier cost based on category"""
        costs = {
            'electronics': 12.99,
            'beauty': 8.99,
            'home': 10.99,
            'fashion': 7.99,
            'sports': 9.99,
            'pet': 6.99,
            'baby': 8.49,
            'general': 9.99
        }
        return costs.get(category, 9.99)
    
    def scan_and_save(self, geo: str = 'US') -> Dict:
        """Full scan and save cycle with auto product creation"""
        db = SessionLocal()
        try:
            trends = self.scan_all(geo=geo)
            saved, created_products = self.save_to_db(trends, db)
            
            return {
                'scanned': {
                    'google': len(trends.get('google', [])),
                    'tiktok': len(trends.get('tiktok', []))
                },
                'total_scanned': sum(len(trends.get(k, [])) for k in trends),
                'new_trends_saved': saved,
                'products_created': len(created_products),
                'created_products': created_products,
                'min_score_threshold': self.min_score_for_product,
                'timestamp': datetime.utcnow().isoformat()
            }
        finally:
            db.close()
    
    def get_recent_trends(self, db: Session, limit: int = 50, min_score: float = None) -> List[Trend]:
        """Get recent trends from database with optional score filter"""
        query = db.query(Trend).order_by(Trend.created_at.desc())
        if min_score:
            query = query.filter(Trend.score >= min_score)
        return query.limit(limit).all()
    
    def create_products_from_trends(self, min_score: float = 80, limit: int = 10) -> Dict:
        """Manually create products from existing trends that meet score threshold"""
        db = SessionLocal()
        try:
            # Get high-score trends that don't have products yet
            trends = db.query(Trend).filter(
                Trend.score >= min_score,
                Trend.product_id.is_(None)
            ).order_by(Trend.score.desc()).limit(limit).all()
            
            created = []
            for trend in trends:
                product = self._create_product_from_trend(trend, db)
                # Update trend with product reference
                trend.product_id = product.id
                created.append({
                    'trend_keyword': trend.keyword,
                    'product_id': product.id,
                    'product_name': product.name,
                    'trend_score': trend.score
                })
            
            db.commit()
            return {
                'trends_processed': len(trends),
                'products_created': len(created),
                'products': created,
                'min_score': min_score
            }
        finally:
            db.close()

    def _add_image_to_product(self, product: Product, db: Session):
        """Додає зображення до продукту при створенні"""
        from app.modules.supplier.image_updater import ImageUpdater
        updater = ImageUpdater()
        updater.auto_update_on_product_creation(db, product)
