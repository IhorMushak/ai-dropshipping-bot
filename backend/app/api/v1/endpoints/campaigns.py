"""
Campaigns API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database import models

router = APIRouter()


@router.get("/")
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    campaigns = db.query(models.Campaign).offset(skip).limit(limit).all()
    return campaigns
