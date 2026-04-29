"""
TikTok Trends source
"""
import logging
from typing import List, Dict
import requests

logger = logging.getLogger(__name__)


class TikTokTrendsSource:
    """TikTok trends integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://open.tiktokapis.com/v2"
    
    def get_trending_hashtags(self) -> List[Dict]:
        """Get trending hashtags from TikTok"""
        results = []
        
        # Тимчасово - тестові дані (без реального API)
        test_trends = [
            {'hashtag': '#cleanwithme', 'views': '1.2B', 'category': 'home'},
            {'hashtag': '#techgadgets', 'views': '890M', 'category': 'electronics'},
            {'hashtag': '#fitnessmotivation', 'views': '2.1B', 'category': 'sports'},
            {'hashtag': '#skincareroutine', 'views': '1.5B', 'category': 'beauty'},
            {'hashtag': '#dogsoftiktok', 'views': '3.2B', 'category': 'pet'},
            {'hashtag': '#momlife', 'views': '980M', 'category': 'baby'},
            {'hashtag': '#fashiontrends', 'views': '1.1B', 'category': 'fashion'},
            {'hashtag': '#amazonfinds', 'views': '2.5B', 'category': 'general'},
        ]
        
        for trend in test_trends:
            results.append({
                'keyword': trend['hashtag'].replace('#', ''),
                'source': 'tiktok',
                'score': self._calculate_score(trend),
                'category': trend['category'],
                'raw_data': trend
            })
        
        logger.info(f"Got {len(results)} trends from TikTok")
        return results
    
    def _calculate_score(self, trend: Dict) -> float:
        """Calculate score based on views"""
        try:
            views_str = trend.get('views', '0B')
            multiplier = 1.0
            if 'B' in views_str:
                multiplier = 1.0
            elif 'M' in views_str:
                multiplier = 0.5
            elif 'K' in views_str:
                multiplier = 0.2
            
            num = float(views_str.replace('B', '').replace('M', '').replace('K', ''))
            score = min(num * multiplier / 10, 95)
            return round(score, 2)
        except:
            return 50.0
