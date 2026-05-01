"""
Періодичні задачі для Celery
"""
import logging
from celery import Celery
from app.core.config import settings

logger = logging.getLogger(__name__)

# Налаштування Celery
celery_app = Celery(
    "ai_dropshipping",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "scan-trends-every-6-hours": {
            "task": "app.tasks.scheduled.scan_trends_task",
            "schedule": 21600.0,  # 6 годин
            "options": {"queue": "trends"}
        },
        "update-metrics-every-hour": {
            "task": "app.tasks.scheduled.update_metrics_task",
            "schedule": 3600.0,  # 1 година
            "options": {"queue": "metrics"}
        }
    }
)


@celery_app.task(name="app.tasks.scheduled.scan_trends_task")
def scan_trends_task():
    """Автоматичне сканування трендів"""
    from app.modules.trend_scanner import TrendScanner
    
    logger.info("🔄 Starting automatic trend scan...")
    scanner = TrendScanner()
    result = scanner.scan_and_save(geo="US")
    
    logger.info(f"✅ Trend scan completed: {result['total_scanned']} trends, {result['products_created']} products")
    return result


@celery_app.task(name="app.tasks.scheduled.update_metrics_task")
def update_metrics_task():
    """Оновлення метрик для дашборду"""
    from app.database.session import SessionLocal
    from app.database.models import Order, Product
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        total_orders = db.query(Order).count()
        revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
        profit = db.query(func.sum(Order.profit)).scalar() or 0
        
        logger.info(f"📊 Metrics updated: orders={total_orders}, revenue=${revenue:.2f}")
        
        # Можна зберігати в окрему таблицю метрик
        return {
            "total_orders": total_orders,
            "revenue": float(revenue),
            "profit": float(profit)
        }
    finally:
        db.close()
