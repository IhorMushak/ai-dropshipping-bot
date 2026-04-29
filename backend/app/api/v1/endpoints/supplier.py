"""
Supplier API endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Product
from app.modules.supplier.dual import DualSupplier
from app.modules.scoring import ProductScorer

router = APIRouter()
supplier = DualSupplier()
scorer = ProductScorer()


@router.get("/supplier/search")
async def search_products(
    keyword: str = Query(..., description="Search keyword"),
    limit: int = Query(20, ge=1, le=50)
):
    """Search products on all platforms"""
    results = supplier.search_all(keyword, limit)
    return results


@router.get("/supplier/search-with-score")
async def search_with_score(
    keyword: str = Query(..., description="Search keyword"),
    trend_score: float = Query(0, ge=0, le=100, description="Trend score for weighting"),
    limit: int = Query(20, ge=1, le=50)
):
    """Search and score products"""
    products = supplier.search_with_scoring(keyword, trend_score, limit)
    return {
        "keyword": keyword,
        "trend_score": trend_score,
        "total": len(products),
        "products": products
    }


@router.post("/products/{product_id}/score")
async def score_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Calculate score for existing product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    
    final_score = scorer.calculate_final_score(product)
    db.commit()
    
    return {
        "product_id": product_id,
        "name": product.name,
        "final_score": final_score,
        "recommendation": scorer.get_recommendation(product),
        "scores": product.scoring_details
    }


@router.get("/products/scoring/stats")
async def get_scoring_stats(db: Session = Depends(get_db)):
    """Get scoring statistics"""
    products = db.query(Product).filter(Product.final_score.isnot(None)).all()
    
    if not products:
        return {"total_scored": 0, "message": "No scored products yet"}
    
    scores = [p.final_score for p in products if p.final_score]
    
    return {
        "total_scored": len(products),
        "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "by_recommendation": {
            "aggressive_scale": len([p for p in products if p.final_score and p.final_score >= 85]),
            "normal_launch": len([p for p in products if p.final_score and 70 <= p.final_score < 85]),
            "test": len([p for p in products if p.final_score and 55 <= p.final_score < 70]),
            "monitor": len([p for p in products if p.final_score and 40 <= p.final_score < 55]),
            "reject": len([p for p in products if p.final_score and p.final_score < 40])
        }
    }
