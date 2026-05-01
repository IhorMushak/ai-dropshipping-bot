"""
Автоматичне оновлення зображень для продуктів
"""
import logging
from sqlalchemy.orm import Session
from app.database.models import Product
from app.modules.supplier.dual import DualSupplier

logger = logging.getLogger(__name__)


class ImageUpdater:
    """Автоматично додає зображення до продуктів"""
    
    def __init__(self):
        self.supplier = DualSupplier()
    
    def update_product_images(self, db: Session, product: Product) -> bool:
        """Оновити зображення для одного продукту"""
        if product.images and len(product.images) > 0:
            return True
        
        keyword = product.name.split('-')[0].strip()
        results = self.supplier.search_all(keyword, limit=1)
        
        image_url = None
        if results.get('aliexpress') and results['aliexpress']:
            image_url = results['aliexpress'][0].get('image_url')
        
        if image_url:
            product.images = [image_url]
            db.commit()
            logger.info(f"✅ Image added for: {product.name}")
            return True
        
        return False
    
    def update_all_missing_images(self, db: Session, limit: int = 20) -> int:
        """Оновити зображення для всіх продуктів без фото"""
        products = db.query(Product).filter(Product.images == None).limit(limit).all()
        
        updated = 0
        for product in products:
            if self.update_product_images(db, product):
                updated += 1
        
        logger.info(f"Updated {updated} products with images")
        return updated
    
    def auto_update_on_product_creation(self, db: Session, product: Product) -> Product:
        """Автоматично додає фото при створенні продукту"""
        keyword = product.name.split('-')[0].strip()
        results = self.supplier.search_all(keyword, limit=1)
        
        if results.get('aliexpress') and results['aliexpress']:
            image_url = results['aliexpress'][0].get('image_url')
            if image_url:
                product.images = [image_url]
                logger.info(f"✅ Auto-added image for new product: {product.name}")
        
        return product
