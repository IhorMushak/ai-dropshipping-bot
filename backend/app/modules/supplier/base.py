"""
Base Supplier class
"""
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class BaseSupplier:
    """Base class for all suppliers"""
    
    def __init__(self, name: str):
        self.name = name
    
    def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        """Search products - to be overridden"""
        return []
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """Get product by ID - to be overridden"""
        return None
