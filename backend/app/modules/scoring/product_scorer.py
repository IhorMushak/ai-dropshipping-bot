"""
Product Scoring Module
Calculates final score for products based on multiple factors
"""
import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.database.models import Product

logger = logging.getLogger(__name__)


class ProductScorer:
    """Calculate product scores"""
    
    def __init__(self):
        self.weights = {
            'trend': 0.35,      # 35% - trend score
            'supplier': 0.25,   # 25% - supplier reliability
            'financial': 0.25,  # 25% - profit margin
            'scalability': 0.15 # 15% - scalability potential
        }
    
    def calculate_final_score(self, product: Product, supplier_data: Optional[Dict] = None) -> float:
        """Calculate final product score (0-100)"""
        scores = {}
        
        # 1. Trend score (0-100)
        scores['trend'] = float(product.trend_score) if product.trend_score else 0
        
        # 2. Supplier score (0-100)
        scores['supplier'] = self._calculate_supplier_score(product, supplier_data)
        
        # 3. Financial score (0-100)
        scores['financial'] = self._calculate_financial_score(product)
        
        # 4. Scalability score (0-100)
        scores['scalability'] = self._calculate_scalability_score(product)
        
        # Calculate weighted final score
        final_score = (
            scores['trend'] * self.weights['trend'] +
            scores['supplier'] * self.weights['supplier'] +
            scores['financial'] * self.weights['financial'] +
            scores['scalability'] * self.weights['scalability']
        )
        
        # Update product with scores
        product.trend_score = scores['trend']
        product.financial_score = scores['financial']
        product.supplier_score = scores['supplier']
        product.scalability_score = scores['scalability']
        product.final_score = final_score
        product.scoring_details = scores
        
        logger.info(f"Product {product.id}: final score = {final_score:.2f}")
        return round(final_score, 2)
    
    def _calculate_supplier_score(self, product: Product, supplier_data: Optional[Dict]) -> float:
        """Calculate supplier reliability score"""
        score = 70  # Default
        
        if product.supplier_rating:
            score = float(product.supplier_rating) * 20  # rating out of 5 -> 0-100
        
        if supplier_data:
            if supplier_data.get('rating'):
                score = supplier_data['rating'] * 20
            if supplier_data.get('sales', 0) > 10000:
                score = min(100, score + 10)
        
        return min(100, max(0, score))
    
    def _calculate_financial_score(self, product: Product) -> float:
        """Calculate financial viability score"""
        score = 50  # Default
        
        if product.selling_price and product.supplier_cost:
            margin = float(product.margin_percent) if product.margin_percent else 0
            
            if margin >= 50:
                score = 100
            elif margin >= 40:
                score = 85
            elif margin >= 30:
                score = 70
            elif margin >= 20:
                score = 50
            else:
                score = 30
        
        return min(100, max(0, score))
    
    def _calculate_scalability_score(self, product: Product) -> float:
        """Calculate scalability potential score"""
        score = 60  # Default
        
        # Based on category (predefined scalability)
        scalable_categories = ['electronics', 'beauty', 'fashion']
        if product.category in scalable_categories:
            score = 85
        
        # Based on price point
        if product.selling_price:
            if 20 <= product.selling_price <= 50:
                score += 10  # Sweet spot price range
        
        return min(100, max(0, score))
    
    def should_scale(self, product: Product) -> bool:
        """Determine if product should be scaled"""
        if product.final_score and product.final_score >= 80:
            return True
        if product.current_roas and product.current_roas >= 2.5:
            return True
        return False
    
    def get_recommendation(self, product: Product) -> str:
        """Get action recommendation based on score"""
        if not product.final_score:
            return "pending_scoring"
        
        if product.final_score >= 85:
            return "aggressive_scale"
        elif product.final_score >= 70:
            return "normal_launch"
        elif product.final_score >= 55:
            return "test_with_small_budget"
        elif product.final_score >= 40:
            return "monitor_and_improve"
        else:
            return "reject_or_rework"
