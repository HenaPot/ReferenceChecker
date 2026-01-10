# File: backend/app/models/credibility_report.py
# Save to: backend/app/models/credibility_report.py

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class CredibilityReport(Base):
    __tablename__ = "credibility_reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_id = Column(UUID(as_uuid=True), ForeignKey("references.reference_id"), unique=True, nullable=False)
    
    # Score components
    domain_score = Column(Integer, nullable=False, default=0)
    metadata_score = Column(Integer, nullable=False, default=0)
    rag_score = Column(Integer, nullable=False, default=0)
    ai_score = Column(Integer, nullable=False, default=0)
    total_score = Column(Integer, nullable=False, default=0)
    
    # Explanations
    domain_explanation = Column(Text, nullable=True)
    metadata_explanation = Column(Text, nullable=True)
    rag_explanation = Column(Text, nullable=True)
    ai_explanation = Column(Text, nullable=True)
    
    # Red flags (stored as JSON array)
    red_flags = Column(JSONB, nullable=True, default=[])
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    reference = relationship("Reference", back_populates="credibility_report")

    def __repr__(self):
        return f"<CredibilityReport for {self.reference_id} (score: {self.total_score})>"