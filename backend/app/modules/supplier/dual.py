"""
Dual Supplier Manager
"""
import logging
from typing import List, Dict
from app.modules.supplier.aliexpress import AliExpressSupplier
from app.modules.supplier.amazon import AmazonSupplier

logger = logging.getLogger(__name__)


class DualSupplier:
    """Manage multiple suppliers"""
    
    def __init__(self):
        self.suppliers = {
            'aliexpress': AliExpressSupplier(),
            'amazon': AmazonSupplier(),
        }
        logger.info("DualSupplier initialized")
    
    def search_all(self, keyword: str, limit: int = 20) -> Dict:
        """Search on all suppliers"""
        results = {
            'keyword': keyword,
            'aliexpress': self.suppliers['aliexpress'].search(keyword, limit),
            'amazon': self.suppliers['amazon'].search(keyword, limit),
            'total': 0
        }
        results['total'] = len(results['aliexpress']) + len(results['amazon'])
        return results
    
    def search_with_scoring(self, keyword: str, trend_score: float = None, limit: int = 20) -> List[Dict]:
        """Search and score products"""
        results = self.search_all(keyword, limit)
        
        all_products = results['aliexpress'] + results['amazon']
        
        # Calculate score for each product
        for product in all_products:
            product['score'] = self._calculate_score(product, trend_score)
        
        # Sort by score
        all_products.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return all_products
    
    def _calculate_score(self, product: Dict, trend_score: float = None) -> float:
        """Calculate product score (0-100)"""
        score = 0
        
        # Rating score (max 30)
        rating = product.get('rating', 0)
        score += (rating / 5) * 30
        
        # Price score (cheaper is better, max 20)
        price = product.get('price', 100)
        price_score = max(0, min(20, (100 - price) / 5))
        score += price_score
        
        # Sales score (max 20)
        sales = product.get('sales', 0)
        sales_score = min(20, sales / 1000)
        score += sales_score
        
        # Trend score if provided (max 30)
        if trend_score:
            score += (trend_score / 100) * 30
        
        return round(min(100, score), 2)
