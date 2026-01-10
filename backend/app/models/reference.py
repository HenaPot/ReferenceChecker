# File: backend/app/models/reference.py
# Save to: backend/app/models/reference.py

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class ReferenceStatus(enum.Enum):
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Reference(Base):
    __tablename__ = "references"

    reference_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    url = Column(String, nullable=False)
    title = Column(String(500), nullable=True)
    author = Column(String(255), nullable=True)
    publication_date = Column(Date, nullable=True)
    domain = Column(String(255), nullable=True, index=True)
    credibility_score = Column(Integer, nullable=True)
    status = Column(SQLEnum(ReferenceStatus), default=ReferenceStatus.processing, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="references")
    credibility_report = relationship("CredibilityReport", back_populates="reference", uselist=False, cascade="all, delete-orphan")
    ratings = relationship("UserRating", back_populates="reference", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Reference {self.url[:50]}... (score: {self.credibility_score})>"