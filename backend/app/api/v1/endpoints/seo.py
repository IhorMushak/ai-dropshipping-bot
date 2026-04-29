from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Product
from app.modules.seo import MediumPublisher, PinterestPublisher

router = APIRouter()
medium = MediumPublisher()
pinterest = PinterestPublisher()


@router.post("/seo/medium/{product_id}")
async def publish_to_medium(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    return medium.publish(product, db)


@router.post("/seo/pinterest/{product_id}")
async def publish_to_pinterest(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    return pinterest.publish(product, db)


@router.get("/seo/article/{product_id}")
async def preview_article(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    return {"article": medium.generate_article(product), "pin": pinterest.generate_pin(product)}
