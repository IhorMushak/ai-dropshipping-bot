"""
AliExpress Supplier - Real API (Omkar Cloud)
Free tier: 5000 requests/month
"""
import logging
import requests
from typing import List, Dict
from app.core.config import settings
from app.modules.supplier.base import BaseSupplier

logger = logging.getLogger(__name__)


class AliExpressSupplier(BaseSupplier):
    """AliExpress supplier integration with real API"""
    
    def __init__(self):
        super().__init__("aliexpress")
        self.api_key = settings.ALIEXPRESS_API_KEY
        self.base_url = "https://aliexpress-scraper-api.omkar.cloud"
        self.has_api_key = bool(self.api_key and self.api_key != "your_omkar_api_key_here")
        
        if not self.has_api_key:
            logger.warning("⚠️ AliExpress API key missing. Get free key from omkar.cloud")
            logger.info("Using mock data mode")
        else:
            logger.info("✅ AliExpress API initialized (real mode)")
    
    def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        """Search products on AliExpress using real API"""
        if not self.has_api_key:
            return self._get_mock_data(keyword, limit)
        
        all_products = []
        pages_to_fetch = max(1, (limit + 19) // 20)  # 20 items per page
        
        for page in range(1, pages_to_fetch + 1):
            try:
                response = requests.get(
                    f"{self.base_url}/aliexpress/search",
                    params={
                        "query": keyword,
                        "page": page
                    },
                    headers={"API-Key": self.api_key},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    for item in results:
                        product = self._parse_product(item)
                        all_products.append(product)
                        
                        if len(all_products) >= limit:
                            break
                    
                    logger.info(f"AliExpress API: page {page} -> {len(results)} products")
                    
                    if len(all_products) >= limit:
                        break
                else:
                    logger.error(f"AliExpress API error: {response.status_code} - {response.text[:200]}")
                    break
                    
            except requests.exceptions.Timeout:
                logger.error("AliExpress API timeout")
                break
            except Exception as e:
                logger.error(f"AliExpress API error: {e}")
                break
        
        if not all_products:
            logger.warning(f"No products found for '{keyword}', using mock data")
            return self._get_mock_data(keyword, limit)
        
        logger.info(f"AliExpress API: total {len(all_products)} products for '{keyword}'")
        return all_products[:limit]
    
    def _parse_product(self, item: Dict) -> Dict:
        """Parse API response according to documentation [citation:1]"""
        return {
            'supplier': 'aliexpress',
            'supplier_product_id': str(item.get('id', '')),
            'title': item.get('title', ''),
            'price': float(item.get('price', 0)),
            'original_price': float(item.get('original_price', 0)) if item.get('original_price') else None,
            'currency': item.get('currency', 'USD'),
            'image_url': item.get('image_url', ''),
            'product_url': f"https://aliexpress.com/item/{item.get('id', '')}.html",
            'rating': float(item.get('rating', 0)) if item.get('rating') else None,
            'rating_count': None,
            'sales': item.get('orders_count', 0),
            'supplier_name': None,
            'shipping_cost': 3.99,
            'shipping_days': '7-15',
            'in_stock': True,
            'discount': item.get('discount', ''),
            'positive_feedback_rate': item.get('positive_feedback_rate', '')
        }
    
    def _get_mock_data(self, keyword: str, limit: int) -> List[Dict]:
        """Fallback mock data when API fails"""
        products = []
        for i in range(min(limit, 10)):
            products.append({
                'supplier': 'aliexpress',
                'supplier_product_id': f'AE_MOCK_{i}',
                'title': f'{keyword.title()} - Premium Quality (Mock Data)',
                'price': round(9.99 + i * 2, 2),
                'original_price': round(19.99 + i * 3, 2) if i % 2 == 0 else None,
                'currency': 'USD',
                'image_url': f'https://example.com/aliexpress/{i}.jpg',
                'product_url': f'https://aliexpress.com/item/mock_{i}.html',
                'rating': round(4.5 + (i % 5) * 0.1, 1),
                'rating_count': 1000 + i * 500,
                'sales': 5000 + i * 1000,
                'supplier_name': f'AliExpress Store {i+1}',
                'shipping_cost': 3.99,
                'shipping_days': '7-15',
                'in_stock': True
            })
        return products
