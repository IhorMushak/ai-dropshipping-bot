# backend/app/database/models/analytics.py

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON, ForeignKey, Numeric, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class Decision(Base, UUIDMixin, TimestampMixin):
    """Every decision the bot makes is logged for learning"""

    __tablename__ = "decisions"

    # Context
    decision_type = Column(String(50), nullable=False)
    decision_context = Column(JSONB, nullable=False)

    # The decision itself
    decision_value = Column(JSONB, nullable=False)

    # Alternatives considered
    alternatives = Column(JSONB)

    # Who made it
    agent_name = Column(String(100))
    model_version = Column(String(50))

    # Tracking
    decision_idempotency = Column(String(200), unique=True)

    # Indexes
    __table_args__ = (
        Index("idx_decisions_type", "decision_type"),
        Index("idx_decisions_created", "created_at"),
        Index("idx_decisions_idempotency", "decision_idempotency"),
    )

    def __repr__(self):
        return f"<Decision(id={self.id}, type={self.decision_type}, created={self.created_at})>"


class RewardLog(Base, UUIDMixin, TimestampMixin):
    """Rewards for reinforcement learning"""

    __tablename__ = "rewards_log"

    decision_id = Column(String(36), ForeignKey("decisions.id", ondelete="CASCADE"))

    # Outcome
    outcome_type = Column(String(50), nullable=False)

    reward_value = Column(Numeric(10, 4), nullable=False)

    # Metrics at outcome time
    metrics_at_outcome = Column(JSONB)

    # Attribution window
    decision_time = Column(DateTime)
    outcome_time = Column(DateTime)

    # For credit assignment
    attribution_weight = Column(Numeric(5, 4), default=1.0)

    # Indexes
    __table_args__ = (
        Index("idx_rewards_decision", "decision_id"),
        Index("idx_rewards_outcome", "outcome_type"),
        Index("idx_rewards_created", "created_at"),
    )


class Event(Base, TimestampMixin):
    """Event sourcing for audit and recovery"""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Event identification
    event_type = Column(String(100), nullable=False)
    event_idempotency = Column(String(200), unique=True)

    # Context
    entity_type = Column(String(50))
    entity_id = Column(String(36))

    # Data
    payload = Column(JSONB, nullable=False)
    error_payload = Column(JSONB)

    # Processing
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending"
    )

    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Timing
    scheduled_for = Column(DateTime, server_default=text("TIMEZONE('utc', NOW())"))
    processed_at = Column(DateTime)

    # Indexes
    __table_args__ = (
        Index("idx_events_status_scheduled", "status", "scheduled_for"),
        Index("idx_events_entity", "entity_type", "entity_id"),
        Index("idx_events_type", "event_type"),
        Index("idx_events_idempotency", "event_idempotency"),
    )
