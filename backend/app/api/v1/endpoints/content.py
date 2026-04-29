"""
Content Generation API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Product
from app.modules.content import ContentGenerator

router = APIRouter()
generator = ContentGenerator()


@router.post("/content/generate/{product_id}")
async def generate_product_content(
    product_id: str,
    model: str = "llama3",
    db: Session = Depends(get_db)
):
    """Generate AI content for a product using local Ollama"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update generator model if specified
    if model:
        generator.model = model
    
    # Generate content
    content = generator.generate_full_product_content(product)
    
    # Save to product
    product.generated_title = content.get('generated_title')
    product.generated_description = content.get('generated_description')
    if content.get('tags'):
        product.tags = content['tags']
    db.commit()
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "generated_title": product.generated_title,
        "generated_description": product.generated_description,
        "tags": product.tags,
        "model_used": generator.model
    }


@router.post("/content/batch-generate")
async def batch_generate_content(
    limit: int = 10,
    status: str = "discovered",
    model: str = "llama3",
    db: Session = Depends(get_db)
):
    """Generate content for multiple products"""
    products = db.query(Product).filter(
        Product.status == status,
        Product.generated_description.is_(None)
    ).limit(limit).all()
    
    generator.model = model
    results = []
    
    for product in products:
        content = generator.generate_full_product_content(product)
        product.generated_title = content.get('generated_title')
        product.generated_description = content.get('generated_description')
        if content.get('tags'):
            product.tags = content['tags']
        results.append({
            "product_id": product.id,
            "product_name": product.name,
            "title": product.generated_title[:50] if product.generated_title else None
        })
    
    db.commit()
    
    return {
        "total_processed": len(results),
        "model": generator.model,
        "products": results
    }


@router.get("/content/models")
async def get_available_models():
    """Get available Ollama models"""
    try:
        import requests
        response = requests.get("http://host.docker.internal:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = [m['name'].split(':')[0] for m in response.json().get('models', [])]
            return {"available_models": models, "current_model": generator.model}
    except:
        pass
    return {"available_models": ["llama3", "mistral", "phi3"], "current_model": generator.model, "note": "Using fallback"}
