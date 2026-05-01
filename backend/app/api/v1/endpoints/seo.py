"""
SEO Parasite API endpoints (Medium + Pinterest)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Product
from app.modules.seo import MediumPublisher, PinterestPublisher

router = APIRouter()
medium = MediumPublisher()
pinterest = PinterestPublisher()


@router.post("/seo/medium/{product_id}")
async def create_medium_article(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Створити SEO-статтю для Medium"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    
    result = medium.publish(product, db)
    return result


@router.post("/seo/pinterest/{product_id}")
async def create_pinterest_pin(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Створити Pinterest пін"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    
    result = pinterest.publish(product, db)
    return result


@router.get("/seo/generate/{product_id}")
async def generate_seo_content(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Згенерувати весь SEO контент для продукту"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    
    return {
        "product_id": product.id,
        "product_name": product.name,
        "medium_article": medium.generate_article(product),
        "pinterest_pin": pinterest.generate_pin(product)
    }
