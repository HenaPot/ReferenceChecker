# File: backend/app/models/user_rating.py
# Save to: backend/app/models/user_rating.py

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class UserRating(Base):
    __tablename__ = "user_ratings"
    __table_args__ = (
        UniqueConstraint('user_id', 'reference_id', name='unique_user_reference_rating'),
    )

    rating_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    reference_id = Column(UUID(as_uuid=True), ForeignKey("references.reference_id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="ratings")
    reference = relationship("Reference", back_populates="ratings")

    def __repr__(self):
        return f"<UserRating {self.rating}/5 for reference {self.reference_id}>"