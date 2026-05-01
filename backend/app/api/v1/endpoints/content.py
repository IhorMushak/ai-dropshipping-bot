"""
Content Generation API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Product
from app.modules.content import ContentGenerator

router = APIRouter()
generator = ContentGenerator()


@router.post("/content/generate/{product_id}")
async def generate_product_content(
    product_id: str,
    model: str = Query("llama3", description="Ollama model name"),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    generator.model = model
    content = generator.generate_full_content(product, db)
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "generated_title": content.get('generated_title'),
        "generated_description": content.get('generated_description'),
        "model_used": generator.model
    }


@router.post("/content/batch-generate")
async def batch_generate_content(
    limit: int = 5,
    status: str = "discovered",
    model: str = "llama3",
    db: Session = Depends(get_db)
):
    products = db.query(Product).filter(Product.status == status).limit(limit).all()
    
    generator.model = model
    results = []
    
    for product in products:
        content = generator.generate_full_content(product, db)
        results.append({
            "product_id": product.id,
            "product_name": product.name,
            "title": content.get('generated_title', '')[:50]
        })
    
    return {
        "total_processed": len(results),
        "model": generator.model,
        "products": results
    }


@router.get("/content/models")
async def get_models():
    """Get available models from Ollama"""
    try:
        import requests
        response = requests.get("http://ollama:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = [m['name'].split(':')[0] for m in response.json().get('models', [])]
            return {"available_models": models, "current_model": generator.model}
    except:
        pass
    return {"available_models": ["llama3", "mistral", "phi3"], "current_model": generator.model, "note": "Using fallback"}
