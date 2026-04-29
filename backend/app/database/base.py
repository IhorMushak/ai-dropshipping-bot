# backend/app/database/base.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String, text
from datetime import datetime
import uuid

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("TIMEZONE('utc', NOW())")
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("TIMEZONE('utc', NOW())"),
        onupdate=datetime.utcnow
    )


class UUIDMixin:
    """Mixin for UUID primary key"""

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )


def generate_uuid() -> str:
    """Generate UUID string"""
    return str(uuid.uuid4())
