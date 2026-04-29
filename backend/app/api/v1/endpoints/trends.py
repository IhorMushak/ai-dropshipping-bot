"""
Trend Scanner API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Trend
from app.modules.trend_scanner import TrendScanner

router = APIRouter()
scanner = TrendScanner()


@router.post("/trends/scan")
async def scan_trends(
    geo: str = Query("US", description="Country code"),
    db: Session = Depends(get_db)
):
    """Scan and save trends from all sources with auto product creation"""
    result = scanner.scan_and_save(geo=geo)
    return result


@router.get("/trends")
async def get_trends(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    source: str = Query(None),
    category: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Trend)
    if source:
        query = query.filter(Trend.source == source)
    if category:
        query = query.filter(Trend.category == category)
    
    total = query.count()
    trends = query.order_by(Trend.score.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "skip": skip, "limit": limit, "items": trends}


@router.get("/trends/categories")
async def get_categories(db: Session = Depends(get_db)):
    from sqlalchemy import func
    categories = db.query(Trend.category, func.count(Trend.id).label('count')).group_by(Trend.category).all()
    return {"categories": [{"name": c[0], "count": c[1]} for c in categories]}
