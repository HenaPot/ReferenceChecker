# File: backend/app/models/rag_source.py
# Save to: backend/app/models/rag_source.py

from sqlalchemy import Column, String, Text, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid
import enum

from app.database import Base


class SourceAddedBy(enum.Enum):
    manual = "manual"
    automated = "automated"
    n8n_crawler = "n8n_crawler"


class RAGSource(Base):
    __tablename__ = "rag_sources"

    source_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, unique=True, nullable=False)
    title = Column(String(500), nullable=True)
    content_text = Column(Text, nullable=True)
    embedding_vector = Column(Vector(384), nullable=True)  # 384 dimensions for sentence-transformers/all-MiniLM-L6-v2
    domain = Column(String(255), nullable=True, index=True)
    credibility_score = Column(Integer, nullable=True)
    added_by = Column(SQLEnum(SourceAddedBy), default=SourceAddedBy.manual, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<RAGSource {self.title[:50]}... (score: {self.credibility_score})>"