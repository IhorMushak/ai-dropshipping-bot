# backend/app/database/models/trend.py

from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, JSON, Index, Numeric, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database.base import Base, TimestampMixin


class Trend(Base, TimestampMixin):
    """Trend data from various sources"""

    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Trend identification
    keyword = Column(String(200), nullable=False)
    source = Column(String(50), nullable=False)

    # Scoring
    score = Column(Float)
    velocity = Column(Float)

    # Metrics
    search_volume = Column(Integer)
    competition = Column(Float)
    growth_rate = Column(Float)

    # Category
    category = Column(String(100))
    subcategory = Column(String(100))

    # Timestamps
    first_detected_at = Column(DateTime)
    last_detected_at = Column(DateTime)
    peak_at = Column(DateTime)

    # Product association
    product_id = Column(String(36))

    # Raw data
    raw_data = Column(JSONB)

    # Indexes
    __table_args__ = (
        Index("idx_trends_keyword", "keyword"),
        Index("idx_trends_source", "source"),
        Index("idx_trends_score", "score"),
        Index("idx_trends_created", "created_at"),
    )


class Config(Base, TimestampMixin):
    """System configuration"""

    __tablename__ = "config"

    id = Column(Integer, primary_key=True, autoincrement=True)

    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(500))

    # Category
    category = Column(String(50), default="general")

    # Editable flag
    is_editable = Column(Boolean, default=True)

    # Indexes
    __table_args__ = (
        Index("idx_config_key", "key"),
        Index("idx_config_category", "category"),
    )


class PriceHistory(Base, TimestampMixin):
    """Price change history for products"""

    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(36), nullable=False)

    old_price = Column(Numeric(10, 2))
    new_price = Column(Numeric(10, 2))
    reason = Column(String(200))

    # Who changed it
    changed_by = Column(String(50), default="system")

    # Performance after change
    subsequent_roas = Column(Numeric(5, 2))

    # Indexes
    __table_args__ = (
        Index("idx_price_history_product", "product_id"),
        Index("idx_price_history_created", "created_at"),
    )
