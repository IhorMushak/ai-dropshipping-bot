# backend/app/database/models/order.py

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Numeric, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class Order(Base, UUIDMixin, TimestampMixin):
    """Order model"""

    __tablename__ = "orders"

    # Identification
    order_number = Column(String(100), unique=True, nullable=False)
    marketplace_order_id = Column(String(200))
    marketplace = Column(String(50), nullable=False)

    # Links
    product_id = Column(String(36), ForeignKey("products.id", ondelete="SET NULL"))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="SET NULL"))

    # Customer info (denormalized for audit)
    customer_name = Column(String(200))
    customer_email = Column(String(200))
    customer_phone = Column(String(50))
    shipping_address = Column(JSONB)
    billing_address = Column(JSONB)

    # NEW: Shipping fields for checkout
    shipping_name = Column(String(200))
    shipping_email = Column(String(200))
    shipping_phone = Column(String(50))
    shipping_address_line1 = Column(String(500))
    shipping_address_line2 = Column(String(500))
    shipping_city = Column(String(100))
    shipping_state = Column(String(100))
    shipping_zip = Column(String(20))
    shipping_country = Column(String(100))
    checkout_status = Column(String(50), default="cart")  # cart, address_collected, payment_pending, completed

    # Order items
    items = Column(JSONB)

    # Financials
    subtotal = Column(Numeric(10, 2), nullable=False)
    shipping_charged = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")

    # Costs
    product_cost = Column(Numeric(10, 2))
    shipping_cost = Column(Numeric(10, 2))
    marketplace_fee = Column(Numeric(10, 2))
    ad_cost_attributed = Column(Numeric(10, 2), default=0)
    total_cost = Column(Numeric(10, 2))
    profit = Column(Numeric(10, 2))

    # Fulfillment
    supplier_id = Column(String(36), ForeignKey("suppliers.id", ondelete="SET NULL"))
    supplier_order_id = Column(String(200))
    tracking_number = Column(String(200))
    tracking_url = Column(Text)
    carrier = Column(String(100))
    estimated_delivery_date = Column(DateTime)
    actual_delivery_date = Column(DateTime)

    # PayPal
    paypal_order_id = Column(String(200))
    paypal_capture_id = Column(String(200))
    paid_amount = Column(Numeric(10, 2))
    paid_at = Column(DateTime)

    # Status
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending"
    )
    # Statuses: pending, confirmed, processing, shipped, delivered,
    #           cancelled, refunded, failed, disputed, checkout_created

    payment_status = Column(String(50), default="pending")
    fulfillment_status = Column(String(50), default="unfulfilled")

    # Refund data
    refund_amount = Column(Numeric(10, 2), default=0)
    refund_reason = Column(Text)
    refunded_at = Column(DateTime)

    # Retry
    retry_count = Column(Integer, default=0)
    next_retry_at = Column(DateTime)

    # Timeline
    order_placed_at = Column(DateTime, nullable=False)
    order_confirmed_at = Column(DateTime)
    processing_started_at = Column(DateTime)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    cancelled_at = Column(DateTime)

    # Notes
    notes = Column(Text)

    # Extra data
    extra_data = Column(JSONB, default={})

    # Relationships
    product = relationship("Product", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    supplier = relationship("Supplier")

    # Indexes
    __table_args__ = (
        Index("idx_orders_order_number", "order_number"),
        Index("idx_orders_status", "status"),
        Index("idx_orders_product", "product_id"),
        Index("idx_orders_customer", "customer_id"),
        Index("idx_orders_placed_at", "order_placed_at"),
        Index("idx_orders_supplier", "supplier_id"),
        Index("idx_orders_tracking", "tracking_number"),
        Index("idx_orders_checkout_status", "checkout_status"),
    )

    def __repr__(self):
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"
