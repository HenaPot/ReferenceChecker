# File: backend/app/models/domain_reputation.py
# Save to: backend/app/models/domain_reputation.py

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.database import Base


class DomainCategory(enum.Enum):
    academic = "academic"
    government = "government"
    news = "news"
    unknown = "unknown"
    unreliable = "unreliable"


class DomainReputation(Base):
    __tablename__ = "domain_reputation"

    domain_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(SQLEnum(DomainCategory), default=DomainCategory.unknown, nullable=False)
    base_score = Column(Integer, nullable=False, default=10)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<DomainReputation {self.domain_name} ({self.category.value}, score: {self.base_score})>"