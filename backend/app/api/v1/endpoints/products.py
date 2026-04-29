"""
Products API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Product

router = APIRouter()


@router.get("/")
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all products with pagination"""
    products = db.query(Product).offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}")
async def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get single product by UUID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/by-status/{status}")
async def get_products_by_status(
    status: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get products by status"""
    products = db.query(Product).filter(Product.status == status).offset(skip).limit(limit).all()
    return {
        "status": status,
        "total": db.query(Product).filter(Product.status == status).count(),
        "items": products
    }
