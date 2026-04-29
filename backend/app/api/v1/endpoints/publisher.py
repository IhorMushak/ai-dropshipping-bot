"""
Publisher API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Product
from app.modules.publisher.webhook_publisher import WebhookPublisher

router = APIRouter()
publisher = WebhookPublisher()


@router.post("/publish/{product_id}")
async def publish_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    result = publisher.publish_product(product, db)
    return result


@router.post("/publish/batch")
async def batch_publish(
    limit: int = Query(5, ge=1, le=20),
    min_score: float = Query(70, ge=0, le=100),
    db: Session = Depends(get_db)
):
    products = db.query(Product).filter(
        Product.status == "discovered",
        Product.final_score >= min_score
    ).limit(limit).all()
    
    results = []
    for product in products:
        result = publisher.publish_product(product, db)
        results.append(result)
    
    return {
        "total": len(results),
        "min_score": min_score,
        "results": results
    }
