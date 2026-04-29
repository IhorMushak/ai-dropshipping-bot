# backend/app/database/models/supplier.py

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Numeric, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class Supplier(Base, UUIDMixin, TimestampMixin):
    """Supplier model"""

    __tablename__ = "suppliers"

    # Identification
    name = Column(String(200), nullable=False)
    platform = Column(String(50), nullable=False)
    external_id = Column(String(200))
    url = Column(Text)

    # Rating & Reliability
    rating = Column(Numeric(3, 2))
    total_reviews = Column(Integer, default=0)
    positive_feedback_percent = Column(Numeric(5, 2))

    # Performance tracking
    total_orders_processed = Column(Integer, default=0)
    successful_orders = Column(Integer, default=0)
    failed_orders = Column(Integer, default=0)
    avg_shipping_days = Column(Numeric(5, 2))
    refund_rate_supplier = Column(Numeric(5, 2), default=0)

    # Capacity
    max_daily_capacity = Column(Integer)
    current_daily_orders = Column(Integer, default=0)

    # Risk flags
    is_risky = Column(Boolean, default=False)
    risk_reason = Column(Text)
    last_failed_at = Column(DateTime)

    # Contact
    contact_name = Column(String(200))
    contact_email = Column(String(200))
    contact_phone = Column(String(50))
    address = Column(Text)

    # API Configuration
    api_key = Column(String(500))
    api_secret = Column(String(500))
    api_endpoint = Column(Text)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Extra data (renamed from 'metadata')
    extra_data = Column(JSONB, default={})

    # Relationships
    product_relations = relationship("ProductSupplier", back_populates="supplier")

    # Indexes
    __table_args__ = (
        Index("idx_suppliers_platform", "platform"),
        Index("idx_suppliers_rating", "rating"),
        Index("idx_suppliers_is_active", "is_active"),
        Index("idx_suppliers_external_id", "external_id"),
    )

    def __repr__(self):
        return f"<Supplier(id={self.id}, name={self.name}, platform={self.platform})>"


class ProductSupplier(Base, UUIDMixin, TimestampMixin):
    """Product-Supplier association"""

    __tablename__ = "product_suppliers"

    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    supplier_id = Column(String(36), ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)

    # Supplier-specific product data
    supplier_sku = Column(String(200), nullable=False)
    supplier_product_id = Column(String(200))
    supplier_price = Column(Numeric(10, 2))
    supplier_shipping_cost = Column(Numeric(10, 2))
    estimated_days = Column(Integer)

    # Priority (1 = primary, 2 = fallback, 3 = tertiary)
    priority = Column(Integer, default=1)

    # Performance
    times_used = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_success_at = Column(DateTime)
    last_failure_at = Column(DateTime)

    # Status
    is_active = Column(Boolean, default=True)
    is_preferred = Column(Boolean, default=False)

    # Extra data
    extra_data = Column(JSONB, default={})

    # Relationships
    product = relationship("Product", back_populates="supplier_relations")
    supplier = relationship("Supplier", back_populates="product_relations")

    # Indexes
    __table_args__ = (
        Index("idx_product_suppliers_product", "product_id"),
        Index("idx_product_suppliers_supplier", "supplier_id"),
        Index("idx_product_suppliers_priority", "priority"),
    )
