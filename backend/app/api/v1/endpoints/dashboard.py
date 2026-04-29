"""
Dashboard API endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/metrics")
async def get_dashboard_metrics():
    return {
        "total_orders": 0,
        "revenue": 0.0,
        "profit": 0.0,
        "conversion_rate": 0.0
    }
