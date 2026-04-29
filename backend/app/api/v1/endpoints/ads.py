"""
Ad Campaign API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Product, Campaign
from app.modules.ads import CampaignCreator

router = APIRouter()
creator = CampaignCreator()


@router.post("/ads/create/{product_id}")
async def create_campaign(
    product_id: str,
    platform: str = Query("meta", regex="^(meta|facebook|tiktok|google)$"),
    db: Session = Depends(get_db)
):
    """Створити рекламну кампанію для продукту"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    result = creator.create_campaign(product, db, platform)
    return result


@router.post("/ads/create-batch")
async def create_batch_campaigns(
    platform: str = Query("meta", regex="^(meta|facebook|tiktok|google)$"),
    limit: int = Query(5, ge=1, le=20),
    min_score: float = Query(70, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """Створити кампанії для топ продуктів"""
    products = db.query(Product).filter(
        Product.status == "published",
        Product.final_score >= min_score
    ).limit(limit).all()
    
    if not products:
        return {"message": "No products found", "campaigns": []}
    
    results = creator.create_batch_campaigns(products, db, platform)
    return {
        "total": len(results),
        "platform": platform,
        "min_score": min_score,
        "campaigns": results
    }


@router.get("/ads/campaigns")
async def get_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Отримати всі рекламні кампанії"""
    campaigns = db.query(Campaign).offset(skip).limit(limit).all()
    return {
        "total": db.query(Campaign).count(),
        "skip": skip,
        "limit": limit,
        "campaigns": campaigns
    }
