"""
Dashboard API endpoints - професійна версія
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database.session import get_db
from app.database.models import Order, Product, Campaign

router = APIRouter()


@router.get("/metrics")
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Отримати основні метрики для дашборду"""
    
    # Загальна кількість замовлень
    total_orders = db.query(Order).count()
    
    # Загальний revenue
    revenue_result = db.query(func.sum(Order.total_amount)).scalar()
    revenue = float(revenue_result) if revenue_result else 0.0
    
    # Загальний прибуток
    profit_result = db.query(func.sum(Order.profit)).scalar()
    profit = float(profit_result) if profit_result else 0.0
    
    # Активні продукти
    active_products = db.query(Product).filter(
        Product.status.in_(['published', 'active'])
    ).count()
    
    # Замовлення за останні 7 днів
    week_ago = datetime.utcnow() - timedelta(days=7)
    orders_last_week = db.query(Order).filter(
        Order.order_placed_at >= week_ago
    ).count()
    
    # Revenue за останні 7 днів
    revenue_last_week_result = db.query(func.sum(Order.total_amount)).filter(
        Order.order_placed_at >= week_ago
    ).scalar()
    revenue_last_week = float(revenue_last_week_result) if revenue_last_week_result else 0.0
    
    # Активні кампанії
    active_campaigns = db.query(Campaign).filter(
        Campaign.status == 'active'
    ).count()
    
    return {
        "total_orders": total_orders,
        "revenue": round(revenue, 2),
        "profit": round(profit, 2),
        "active_products": active_products,
        "orders_last_week": orders_last_week,
        "revenue_last_week": round(revenue_last_week, 2),
        "active_campaigns": active_campaigns,
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/recent-activity")
async def get_recent_activity(db: Session = Depends(get_db)):
    """Отримати останню активність"""
    
    recent_orders = db.query(Order).order_by(
        Order.order_placed_at.desc()
    ).limit(5).all()
    
    recent_products = db.query(Product).order_by(
        Product.created_at.desc()
    ).limit(5).all()
    
    return {
        "recent_orders": [
            {
                "order_number": o.order_number,
                "total_amount": float(o.total_amount) if o.total_amount else 0,
                "status": o.status,
                "date": o.order_placed_at.isoformat() if o.order_placed_at else None
            } for o in recent_orders
        ],
        "recent_products": [
            {
                "name": p.name,
                "status": p.status,
                "score": float(p.final_score) if p.final_score else None,
                "date": p.created_at.isoformat() if p.created_at else None
            } for p in recent_products
        ]
    }


@router.get("/sales-trend")
async def get_sales_trend(db: Session = Depends(get_db)):
    """Отримати тренд продажів за останні 30 днів"""
    
    daily_sales = []
    for i in range(30):
        date = datetime.utcnow().date() - timedelta(days=i)
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        daily_total = db.query(func.sum(Order.total_amount)).filter(
            Order.order_placed_at >= start,
            Order.order_placed_at <= end
        ).scalar()
        
        daily_sales.append({
            "date": date.isoformat(),
            "revenue": float(daily_total) if daily_total else 0.0,
            "orders": db.query(Order).filter(
                Order.order_placed_at >= start,
                Order.order_placed_at <= end
            ).count()
        })
    
    return {"daily_sales": daily_sales}
