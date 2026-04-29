# backend/app/database/models/product.py

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Index, Numeric, text
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.base import Base, TimestampMixin, UUIDMixin


class Product(Base, UUIDMixin, TimestampMixin):
    """Product model - core entity"""

    __tablename__ = "products"

    # Basic Information
    name = Column(String(500), nullable=False)
    description = Column(Text)
    short_description = Column(String(500))
    category = Column(String(100))
    subcategory = Column(String(100))
    sku = Column(String(100), unique=True)

    # Financials
    supplier_cost = Column(Numeric(10, 2), nullable=False)
    shipping_cost = Column(Numeric(10, 2), default=0.0)
    total_cost = Column(Numeric(10, 2))
    selling_price = Column(Numeric(10, 2))
    compare_at_price = Column(Numeric(10, 2))
    margin_percent = Column(Numeric(5, 2))

    # Scoring (0-100)
    trend_score = Column(Numeric(5, 2))
    financial_score = Column(Numeric(5, 2))
    supplier_score = Column(Numeric(5, 2))
    scalability_score = Column(Numeric(5, 2))
    final_score = Column(Numeric(5, 2))
    scoring_details = Column(JSONB)

    # Supplier Information
    supplier_id = Column(String(200))
    supplier_sku = Column(String(200))
    supplier_name = Column(String(200))
    supplier_rating = Column(Numeric(3, 2))
    supplier_reviews = Column(Integer)
    supplier_total_orders = Column(Integer, default=0)
    shipping_days_estimate = Column(Integer)

    # Content
    images = Column(JSONB)
    video_url = Column(Text)
    generated_title = Column(String(500))
    generated_description = Column(Text)
    seo_title = Column(String(500))
    seo_description = Column(String(500))
    tags = Column(ARRAY(String))
    bullet_points = Column(JSONB)

    # Marketplace (Shopify)
    shopify_product_id = Column(String(100))
    shopify_variant_id = Column(String(100))
    shopify_handle = Column(String(200))

    # Status
    status = Column(
        String(50),
        nullable=False,
        default="discovered",
        server_default="discovered"
    )
    # Statuses: discovered, validating, validated, rejected,
    #           publishing, published, active, paused, scaling,
    #           optimizing, archived, failed

    status_reason = Column(Text)
    status_updated_at = Column(DateTime, server_default=text("TIMEZONE('utc', NOW())"))

    # Lifecycle timestamps
    discovered_at = Column(DateTime, server_default=text("TIMEZONE('utc', NOW())"))
    validated_at = Column(DateTime)
    published_at = Column(DateTime)
    first_sale_at = Column(DateTime)
    last_sale_at = Column(DateTime)
    archived_at = Column(DateTime)

    # Performance metrics (denormalized)
    total_sales = Column(Integer, default=0)
    total_revenue = Column(Numeric(12, 2), default=0)
    total_profit = Column(Numeric(12, 2), default=0)
    total_ad_spend = Column(Numeric(12, 2), default=0)
    total_refunds = Column(Integer, default=0)
    refund_rate = Column(Numeric(5, 2))
    current_roas = Column(Numeric(5, 2))

    # Scaling
    scale_level = Column(Integer, default=1)
    scaled_at = Column(DateTime)

    # Extra data (renamed from 'metadata' to avoid conflict)
    extra_data = Column(JSONB, default={})

    # Relationships
    orders = relationship("Order", back_populates="product", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="product", cascade="all, delete-orphan")
    supplier_relations = relationship("ProductSupplier", back_populates="product", cascade="all, delete-orphan")
    # price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_products_status", "status"),
        Index("idx_products_final_score", "final_score"),
        Index("idx_products_category", "category"),
        Index("idx_products_created_at", "created_at"),
        Index("idx_products_current_roas", "current_roas"),
        Index("idx_products_shopify_id", "shopify_product_id"),
        Index("idx_products_sku", "sku"),
    )

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name[:50]}, status={self.status})>"
