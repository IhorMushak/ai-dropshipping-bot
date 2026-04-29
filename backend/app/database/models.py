# backend/app/database/models.py

from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(100))

    # Financials
    supplier_cost = Column(Float)
    shipping_cost = Column(Float)
    total_cost = Column(Float)
    selling_price = Column(Float)
    margin_percent = Column(Float)

    # Scoring
    trend_score = Column(Float)
    financial_score = Column(Float)
    final_score = Column(Float)

    # Supplier
    supplier_id = Column(String(200))
    supplier_sku = Column(String(200))
    supplier_rating = Column(Float)
    shipping_days = Column(Integer)

    # Content
    images = Column(JSON)  # List of URLs
    generated_title = Column(String(500))
    generated_description = Column(Text)

    # Marketplace
    shopify_product_id = Column(String(100))
    shopify_handle = Column(String(200))

    # Status
    status = Column(String(50), default="discovered")
    # discovered, validated, published, active, paused, archived

    # Metrics
    total_sales = Column(Integer, default=0)
    total_revenue = Column(Float, default=0)
    total_ad_spend = Column(Float, default=0)
    current_roas = Column(Float)

    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="product")
    campaigns = relationship("Campaign", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number = Column(String(100), unique=True, nullable=False)

    # Links
    product_id = Column(String(36), ForeignKey("products.id"))
    product = relationship("Product", back_populates="orders")

    # Customer
    customer_name = Column(String(200))
    customer_email = Column(String(200))
    shipping_address = Column(JSON)

    # Financials
    subtotal = Column(Float)
    shipping_charged = Column(Float)
    total_amount = Column(Float)

    # Costs
    product_cost = Column(Float)
    shipping_cost = Column(Float)
    ad_cost = Column(Float)
    profit = Column(Float)

    # Fulfillment
    supplier_order_id = Column(String(200))
    tracking_number = Column(String(200))
    tracking_url = Column(Text)

    # Status
    status = Column(String(50), default="pending")
    # pending, processing, shipped, delivered, refunded, failed

    # Timestamps
    order_placed_at = Column(DateTime)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id"))
    product = relationship("Product", back_populates="campaigns")

    # Platform
    platform = Column(String(50), default="meta")  # meta, tiktok, google

    # External IDs
    ad_account_id = Column(String(100))
    campaign_id = Column(String(100))
    ad_set_id = Column(String(100))
    ad_id = Column(String(100))

    # Creative
    headline = Column(String(200))
    primary_text = Column(Text)
    image_url = Column(Text)
    video_url = Column(Text)

    # Budget
    daily_budget = Column(Float)
    total_spend = Column(Float, default=0)

    # Status
    status = Column(String(50), default="draft")
    # draft, active, paused, ended

    # Metrics (cached)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0)

    # Timestamps
    launched_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdMetric(Base):
    __tablename__ = "ad_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"))

    date = Column(DateTime)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)


class Trend(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(200))
    source = Column(String(50))  # google, tiktok
    score = Column(Float)

    # Metrics at discovery
    search_volume = Column(Integer)
    competition = Column(Float)

    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)


class Config(Base):
    __tablename__ = "config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True)
    value = Column(Text)
    description = Column(String(500))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
