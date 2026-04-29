# backend/app/database/models/campaign.py

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Numeric, Date, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class Campaign(Base, UUIDMixin, TimestampMixin):
    """Ad Campaign model"""

    __tablename__ = "campaigns"

    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)

    # Platform
    platform = Column(String(50), nullable=False)  # meta, tiktok, google

    # External IDs
    ad_account_id = Column(String(100))
    campaign_id = Column(String(100))
    ad_set_id = Column(String(100))
    ad_id = Column(String(100))

    # Creative
    creative_type = Column(String(50))  # image, video, carousel
    headline = Column(String(200))
    primary_text = Column(Text)
    description = Column(String(500))
    call_to_action = Column(String(50))
    image_url = Column(Text)
    video_url = Column(Text)
    creative_hash = Column(String(100))

    # Targeting
    target_audience = Column(JSONB)
    interests = Column(JSONB)
    locations = Column(JSONB)
    age_range = Column(JSONB)
    genders = Column(JSONB)

    # Budget
    daily_budget = Column(Numeric(10, 2))
    lifetime_budget = Column(Numeric(10, 2))
    current_budget = Column(Numeric(10, 2))
    bid_strategy = Column(String(50))  # lowest_cost, target_cost, highest_value
    bid_amount = Column(Numeric(10, 2))

    # Performance (cached)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Numeric(10, 2), default=0)
    conversions = Column(Integer, default=0)
    conversion_value = Column(Numeric(10, 2), default=0)
    ctr = Column(Numeric(5, 4))
    cpc = Column(Numeric(10, 4))
    roas = Column(Numeric(5, 2))

    # Status
    status = Column(
        String(50),
        nullable=False,
        default="draft",
        server_default="draft"
    )
    # Statuses: draft, active, paused, ended, rejected, archived

    # A/B Testing
    is_ab_test = Column(Boolean, default=False)
    ab_test_variant = Column(String(10))  # A, B, C, control
    ab_test_group = Column(String(50))

    # Timestamps
    launched_at = Column(DateTime)
    paused_at = Column(DateTime)
    ended_at = Column(DateTime)

    # Extra data (renamed from 'metadata' to avoid conflict)
    extra_data = Column(JSONB, default={})

    # Relationships
    product = relationship("Product", back_populates="campaigns")
    metrics = relationship("AdMetric", back_populates="campaign", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_campaigns_product", "product_id"),
        Index("idx_campaigns_status", "status"),
        Index("idx_campaigns_platform", "platform"),
        Index("idx_campaigns_roas", "roas"),
        Index("idx_campaigns_external_id", "campaign_id"),
    )

    def __repr__(self):
        return f"<Campaign(id={self.id}, product_id={self.product_id}, status={self.status})>"


class AdMetric(Base, TimestampMixin):
    """Daily ad metrics for campaigns"""

    __tablename__ = "ad_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)

    # Date aggregation
    date = Column(Date, nullable=False)

    # Core metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Numeric(10, 2), default=0)

    # Conversion metrics
    conversions = Column(Integer, default=0)
    conversion_value = Column(Numeric(10, 2), default=0)

    # Calculated
    ctr = Column(Numeric(5, 4))
    cpc = Column(Numeric(10, 4))
    cpm = Column(Numeric(10, 2))
    roas = Column(Numeric(5, 2))

    # Attribution
    attributed_order_ids = Column(JSONB, default=[])

    # Breakdowns
    breakdown_age = Column(JSONB)
    breakdown_gender = Column(JSONB)
    breakdown_platform = Column(JSONB)
    breakdown_device = Column(JSONB)
    breakdown_region = Column(JSONB)

    # Relationships
    campaign = relationship("Campaign", back_populates="metrics")

    # Indexes
    __table_args__ = (
        Index("idx_ad_metrics_campaign_date", "campaign_id", "date", unique=True),
        Index("idx_ad_metrics_date", "date"),
    )

    def __repr__(self):
        return f"<AdMetric(campaign_id={self.campaign_id}, date={self.date}, spend={self.spend})>"
