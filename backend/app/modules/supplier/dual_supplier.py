"""
Dual Supplier Integration
AliExpress (Omkar Cloud) + Amazon (WebScrapingAPI)
"""
import logging
import requests
from typing import List, Dict, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class DualSupplier:
    """Unified interface for AliExpress and Amazon"""
    
    def __init__(self):
        self.aliexpress_key = settings.ALIEXPRESS_API_KEY
        self.amazon_key = settings.AMAZON_API_KEY
        self.aliexpress_available = bool(self.aliexpress_key)
        self.amazon_available = bool(self.amazon_key)
        
        if not self.aliexpress_available:
            logger.warning("AliExpress API key missing. Get free key from omkar.cloud")
        if not self.amazon_available:
            logger.warning("Amazon API key missing. Get free key from webscrapingapi.com")
    
    # ============ AliExpress (Omkar Cloud) ============
    
    def search_aliexpress(self, keyword: str, limit: int = 20) -> List[Dict]:
        """Search products on AliExpress"""
        if not self.aliexpress_available:
            return self._mock_aliexpress(keyword, limit)
        
        try:
            response = requests.get(
                "https://aliexpress-scraper-api.omkar.cloud/aliexpress/search",
                params={"query": keyword},
                headers={"API-Key": self.aliexpress_key},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                products = self._parse_aliexpress_results(data, limit)
                logger.info(f"AliExpress: {len(products)} products for '{keyword}'")
                return products
            else:
                logger.error(f"AliExpress API error: {response.status_code}")
                return self._mock_aliexpress(keyword, limit)
                
        except Exception as e:
            logger.error(f"Error searching AliExpress: {e}")
            return self._mock_aliexpress(keyword, limit)
    
    def _parse_aliexpress_results(self, data: Dict, limit: int) -> List[Dict]:
        """Parse AliExpress API response"""
        products = []
        items = data.get('items', data.get('products', []))
        
        for item in items[:limit]:
            product = {
                'source': 'aliexpress',
                'supplier_product_id': str(item.get('productId', item.get('id', ''))),
                'title': item.get('productTitle', item.get('title', '')),
                'price': self._extract_price(item),
                'original_price': self._extract_original_price(item),
                'currency': 'USD',
                'image_url': item.get('imageUrl', item.get('image', '')),
                'product_url': item.get('productUrl', item.get('url', '')),
                'rating': item.get('evaluationScore', item.get('rating', 0)),
                'sales': item.get('orders', item.get('sold', 0)),
                'supplier_name': item.get('storeName', item.get('seller', '')),
                'in_stock': True
            }
            products.append(product)
        
        return products
    
    # ============ Amazon (WebScrapingAPI) ============
    
    def search_amazon(self, keyword: str, limit: int = 20) -> List[Dict]:
        """Search products on Amazon"""
        if not self.amazon_available:
            return self._mock_amazon(keyword, limit)
        
        try:
            # Amazon search URL
            search_url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
            
            response = requests.get(
                "https://api.webscrapingapi.com/v1",
                params={
                    'api_key': self.amazon_key,
                    'url': search_url,
                    'render_js': 1,
                    'country_code': 'us'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                products = self._parse_amazon_response(response.text, limit)
                logger.info(f"Amazon: {len(products)} products for '{keyword}'")
                return products
            else:
                logger.error(f"Amazon API error: {response.status_code}")
                return self._mock_amazon(keyword, limit)
                
        except Exception as e:
            logger.error(f"Error searching Amazon: {e}")
            return self._mock_amazon(keyword, limit)
    
    def _parse_amazon_response(self, html: str, limit: int) -> List[Dict]:
        """Parse Amazon HTML response"""
        # Simple regex parsing (for MVP)
        import re
        
        products = []
        pattern = r'data-asin="([^"]+)"'
        asins = re.findall(pattern, html)[:limit]
        
        title_pattern = r'<span class="a-size-medium a-color-base a-text-normal">([^<]+)</span>'
        titles = re.findall(title_pattern, html)[:limit]
        
        price_pattern = r'<span class="a-price-whole">(\d+)</span>'
        prices = re.findall(price_pattern, html)[:limit]
        
        for i, asin in enumerate(asins):
            product = {
                'source': 'amazon',
                'supplier_product_id': asin,
                'title': titles[i] if i < len(titles) else f"{keyword} Product",
                'price': float(prices[i]) if i < len(prices) else 19.99,
                'original_price': None,
                'currency': 'USD',
                'image_url': f"https://images-na.ssl-images-amazon.com/images/P/{asin}.01.L.jpg",
                'product_url': f"https://www.amazon.com/dp/{asin}",
                'rating': 4.5,
                'sales': 0,
                'supplier_name': 'Amazon',
                'in_stock': True
            }
            products.append(product)
        
        return products
    
    # ============ Unified Search ============
    
    def search_all(self, keyword: str, limit: int = 20) -> Dict:
        """Search on all available platforms"""
        results = {
            'keyword': keyword,
            'aliexpress': self.search_aliexpress(keyword, limit),
            'amazon': self.search_amazon(keyword, limit),
            'total': 0
        }
        results['total'] = len(results['aliexpress']) + len(results['amazon'])
        return results
    
    def search_by_trend(self, trend_keyword: str, trend_score: float) -> Dict:
        """Search products for a trend and return with scores"""
        results = self.search_all(trend_keyword, limit=10)
        
        # Add trend score to each product for ranking
        for product in results['aliexpress']:
            product['trend_keyword'] = trend_keyword
            product['trend_score'] = trend_score
            product['combined_score'] = self._calculate_combined_score(product, trend_score)
        
        for product in results['amazon']:
            product['trend_keyword'] = trend_keyword
            product['trend_score'] = trend_score
            product['combined_score'] = self._calculate_combined_score(product, trend_score)
        
        return results
    
    def _calculate_combined_score(self, product: Dict, trend_score: float) -> float:
        """Calculate combined score based on product metrics and trend"""
        # Base score from product rating (max 30)
        rating_score = (product.get('rating', 0) / 5) * 30
        
        # Price score (cheaper is better, max 20)
        price = product.get('price', 100)
        price_score = max(0, min(20, (100 - price) / 5))
        
        # Trend score contributes 50%
        trend_contribution = trend_score * 0.5
        
        # Total score out of 100
        total = rating_score + price_score + trend_contribution
        return round(min(100, total), 2)
    
    # ============ Helper Methods ============
    
    def _extract_price(self, item: Dict) -> float:
        """Extract price from item"""
        price = item.get('salePrice', item.get('price', item.get('minPrice', '0')))
        if isinstance(price, str):
            price = price.replace('$', '').replace('US', '').strip()
        try:
            return float(price)
        except:
            return 0.0
    
    def _extract_original_price(self, item: Dict) -> Optional[float]:
        """Extract original price"""
        orig = item.get('originalPrice', item.get('listPrice', None))
        if orig:
            if isinstance(orig, str):
                orig = orig.replace('$', '').strip()
            try:
                return float(orig)
            except:
                pass
        return None
    
    # ============ Mock Data (for testing without API keys) ============
    
    def _mock_aliexpress(self, keyword: str, limit: int) -> List[Dict]:
        """Mock AliExpress data for testing"""
        return [{
            'source': 'aliexpress',
            'supplier_product_id': f'AE_{i}',
            'title': f'{keyword.title()} - Premium Quality',
            'price': 15.99,
            'original_price': 29.99,
            'currency': 'USD',
            'image_url': f'https://example.com/ae/{keyword}.jpg',
            'product_url': f'https://aliexpress.com/item/AE_{i}.html',
            'rating': 4.7,
            'sales': 5000,
            'supplier_name': 'Top Global Store',
            'in_stock': True
        } for i in range(min(limit, 10))]
    
    def _mock_amazon(self, keyword: str, limit: int) -> List[Dict]:
        """Mock Amazon data for testing"""
        return [{
            'source': 'amazon',
            'supplier_product_id': f'B0{i}XYZ',
            'title': f'{keyword.title()} - Best Seller',
            'price': 24.99,
            'original_price': 49.99,
            'currency': 'USD',
            'image_url': f'https://example.com/amz/{keyword}.jpg',
            'product_url': f'https://amazon.com/dp/B0{i}XYZ',
            'rating': 4.5,
            'sales': 12000,
            'supplier_name': 'Amazon Seller',
            'in_stock': True
        } for i in range(min(limit, 10))]
