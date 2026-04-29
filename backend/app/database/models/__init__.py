# backend/app/database/models/__init__.py

from app.database.models.product import Product
from app.database.models.supplier import Supplier, ProductSupplier
from app.database.models.order import Order
from app.database.models.customer import Customer
from app.database.models.campaign import Campaign, AdMetric
from app.database.models.analytics import Decision, RewardLog, Event
from app.database.models.trend import Trend, Config, PriceHistory

__all__ = [
    "Product",
    "Supplier",
    "ProductSupplier",
    "Order",
    "Customer",
    "Campaign",
    "AdMetric",
    "Decision",
    "RewardLog",
    "Event",
    "Trend",
    "Config",
    "PriceHistory",
]
