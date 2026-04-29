"""
Amazon Supplier - Real API (WebScrapingAPI)
Free tier: 5000 requests/month
"""
import logging
import requests
import re
from typing import List, Dict
from app.core.config import settings
from app.modules.supplier.base import BaseSupplier

logger = logging.getLogger(__name__)


class AmazonSupplier(BaseSupplier):
    """Amazon supplier integration with real API"""
    
    def __init__(self):
        super().__init__("amazon")
        self.api_key = settings.AMAZON_API_KEY
        self.base_url = "https://api.webscrapingapi.com/v1"
        self.has_api_key = bool(self.api_key and self.api_key != "your_webscrapingapi_key_here")
        
        if not self.has_api_key:
            logger.warning("⚠️ Amazon API key missing. Get free key from webscrapingapi.com")
            logger.info("Using mock data mode")
        else:
            logger.info("✅ Amazon API initialized (real mode)")
    
    def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        """Search products on Amazon using real API"""
        if not self.has_api_key:
            return self._get_mock_data(keyword, limit)
        
        try:
            # Build Amazon search URL
            search_url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
            
            response = requests.get(
                self.base_url,
                params={
                    'api_key': self.api_key,
                    'url': search_url,
                    'render_js': 1,
                    'country_code': 'us',
                    'premium_proxy': 1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                products = self._parse_html(response.text, limit)
                logger.info(f"Amazon API: found {len(products)} products for '{keyword}'")
                return products
            else:
                logger.error(f"Amazon API error: {response.status_code}")
                return self._get_mock_data(keyword, limit)
                
        except requests.exceptions.Timeout:
            logger.error("Amazon API timeout")
            return self._get_mock_data(keyword, limit)
        except Exception as e:
            logger.error(f"Amazon API error: {e}")
            return self._get_mock_data(keyword, limit)
    
    def _parse_html(self, html: str, limit: int) -> List[Dict]:
        """Parse Amazon HTML response"""
        products = []
        
        # Extract ASINs
        asin_pattern = r'data-asin="([^"]+)"'
        asins = re.findall(asin_pattern, html)[:limit]
        
        # Extract titles
        title_pattern = r'<span class="a-size-medium a-color-base a-text-normal">([^<]+)</span>'
        titles = re.findall(title_pattern, html)[:limit]
        
        # Extract prices
        price_pattern = r'<span class="a-price-whole">(\d+)</span><span class="a-price-fraction">(\d+)</span>'
        prices = re.findall(price_pattern, html)[:limit]
        
        # Extract ratings
        rating_pattern = r'<span class="a-icon-alt">([\d.]+) out of 5 stars</span>'
        ratings = re.findall(rating_pattern, html)[:limit]
        
        # Extract review counts
        review_pattern = r'<span class="a-size-base s-underline-text">([\d,]+)</span>'
        reviews = re.findall(review_pattern, html)[:limit]
        
        for i, asin in enumerate(asins):
            price = 0.0
            if i < len(prices) and prices[i]:
                price = float(f"{prices[i][0]}.{prices[i][1]}")
            
            rating = 4.5
            if i < len(ratings):
                try:
                    rating = float(ratings[i])
                except:
                    pass
            
            review_count = 1000
            if i < len(reviews):
                try:
                    review_count = int(reviews[i].replace(',', ''))
                except:
                    pass
            
            products.append({
                'supplier': 'amazon',
                'supplier_product_id': asin,
                'title': titles[i] if i < len(titles) else f"{keyword.title()} Product",
                'price': price,
                'original_price': None,
                'currency': 'USD',
                'image_url': f"https://images-na.ssl-images-amazon.com/images/P/{asin}.01.L.jpg",
                'product_url': f"https://www.amazon.com/dp/{asin}",
                'rating': rating,
                'rating_count': review_count,
                'sales': review_count,
                'supplier_name': 'Amazon',
                'shipping_cost': 0.0,
                'shipping_days': '2-5',
                'in_stock': True
            })
        
        return products
    
    def _get_mock_data(self, keyword: str, limit: int) -> List[Dict]:
        """Fallback mock data when API fails"""
        products = []
        for i in range(min(limit, 10)):
            products.append({
                'supplier': 'amazon',
                'supplier_product_id': f'B0{i}XYZ_MOCK',
                'title': f'{keyword.title()} - Best Seller (Mock Data)',
                'price': round(19.99 + i * 3, 2),
                'original_price': round(39.99 + i * 5, 2) if i % 2 == 0 else None,
                'currency': 'USD',
                'image_url': f'https://example.com/amazon/{i}.jpg',
                'product_url': f'https://amazon.com/dp/mock_{i}',
                'rating': round(4.3 + (i % 5) * 0.1, 1),
                'rating_count': 5000 + i * 1000,
                'sales': 15000 + i * 2000,
                'supplier_name': 'Amazon Seller',
                'shipping_cost': 0.0,
                'shipping_days': '2-5',
                'in_stock': True
            })
        return products
