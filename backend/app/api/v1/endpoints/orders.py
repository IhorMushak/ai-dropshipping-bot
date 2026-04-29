"""
Orders API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database import models

router = APIRouter()


@router.get("/")
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    return orders
