"""
InfluenceFlow API endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Product
from app.modules.influence import InfluenceFlowAPI

router = APIRouter()
influence = InfluenceFlowAPI()


@router.get("/influence/search")
async def search_influencers(
    niche: str = Query(None, description="Категорія/ніша"),
    min_followers: int = Query(10000, ge=1000),
    max_followers: int = Query(100000, le=1000000),
    limit: int = Query(20, ge=1, le=50)
):
    """Пошук інфлюенсерів за нішею"""
    results = influence.search_influencers(
        niche=niche,
        min_followers=min_followers,
        max_followers=max_followers,
        limit=limit
    )
    return {
        "total": len(results),
        "niche": niche,
        "influencers": results
    }


@router.post("/influence/campaign/{product_id}")
async def create_influence_campaign(
    product_id: str,
    budget: float = Query(500, ge=100, le=10000),
    influencers_needed: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """Створити інфлюенс-кампанію для продукту"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    
    result = influence.create_influence_campaign(
        product=product,
        budget=budget,
        influencers_needed=influencers_needed
    )
    return result


@router.get("/influence/status/{campaign_id}")
async def get_campaign_status(campaign_id: str):
    """Отримати статус кампанії"""
    result = influence.get_campaign_status(campaign_id)
    return result or {"error": "Campaign not found"}
