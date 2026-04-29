# backend/app/database/models/customer.py

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Numeric, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class Customer(Base, UUIDMixin, TimestampMixin):
    """Customer model"""

    __tablename__ = "customers"

    # Basic info
    email = Column(String(200), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50))

    # Addresses
    default_address = Column(JSONB)
    addresses = Column(JSONB, default=[])

    # Marketing
    accepts_marketing = Column(Boolean, default=False)
    marketing_opt_in_at = Column(DateTime)

    # Lifetime metrics
    total_orders = Column(Integer, default=0)
    total_spent = Column(Numeric(12, 2), default=0)
    average_order_value = Column(Numeric(10, 2))
    last_order_at = Column(DateTime)

    # Segmentation
    customer_segment = Column(String(50))
    lifetime_value_tier = Column(String(20))
    churn_risk_score = Column(Numeric(5, 2))

    # Preferences
    preferred_categories = Column(JSONB, default=[])
    preferred_price_range = Column(JSONB)

    # Status
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(Text)

    # External IDs
    shopify_customer_id = Column(String(100))
    stripe_customer_id = Column(String(100))

    # Extra data
    extra_data = Column(JSONB, default={})

    # Relationships
    orders = relationship("Order", back_populates="customer")

    # Indexes
    __table_args__ = (
        Index("idx_customers_email", "email"),
        Index("idx_customers_segment", "customer_segment"),
        Index("idx_customers_total_spent", "total_spent"),
        Index("idx_customers_last_order", "last_order_at"),
        Index("idx_customers_shopify_id", "shopify_customer_id"),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def __repr__(self):
        return f"<Customer(id={self.id}, email={self.email}, segment={self.customer_segment})>"
