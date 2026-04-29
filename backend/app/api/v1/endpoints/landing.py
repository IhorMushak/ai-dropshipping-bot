"""
Landing Page API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Product
from app.modules.publisher.landing import LandingPageGenerator

router = APIRouter()
generator = LandingPageGenerator()


@router.post("/landing/generate/{product_id}")
async def generate_landing(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Generate landing page for product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    result = generator.generate(product, db)
    return result


@router.get("/landing/{page_id}")
async def view_landing(page_id: str):
    """View generated landing page"""
    import os
    file_path = f"/tmp/landings/{page_id}.html"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Page not found")
    
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)
