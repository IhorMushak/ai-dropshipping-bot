"""
API v1 router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    products, orders, campaigns, dashboard, supplier, 
    content, publisher, ads, order_processor, support, trends
)

api_router = APIRouter()

api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(supplier.router, prefix="", tags=["supplier"])
api_router.include_router(content.router, prefix="", tags=["content"])
api_router.include_router(publisher.router, prefix="", tags=["publisher"])
api_router.include_router(ads.router, prefix="", tags=["ads"])
api_router.include_router(order_processor.router, prefix="", tags=["order_processor"])
api_router.include_router(support.router, prefix="", tags=["support"])
api_router.include_router(trends.router, prefix="", tags=["trends"])
from app.api.v1.endpoints import landing
api_router.include_router(landing.router, prefix="", tags=["landing"])
from app.api.v1.endpoints import payment
api_router.include_router(payment.router, prefix="", tags=["payment"])
from app.api.v1.endpoints import seo
api_router.include_router(seo.router, prefix="", tags=["seo"])
