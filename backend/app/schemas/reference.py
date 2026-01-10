# File: backend/app/schemas/reference.py

from pydantic import BaseModel, HttpUrl
from datetime import datetime, date
from uuid import UUID
from typing import Optional


class ReferenceCreate(BaseModel):
    url: str


class ReferenceResponse(BaseModel):
    reference_id: UUID
    url: str
    title: Optional[str]
    author: Optional[str]
    publication_date: Optional[date]
    domain: Optional[str]
    credibility_score: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CredibilityReportResponse(BaseModel):
    report_id: UUID
    reference_id: UUID
    domain_score: int
    metadata_score: int
    rag_score: int
    ai_score: int
    total_score: int
    domain_explanation: Optional[str]
    metadata_explanation: Optional[str]
    rag_explanation: Optional[str]
    ai_explanation: Optional[str]
    red_flags: list
    created_at: datetime

    class Config:
        from_attributes = True


class ReferenceDetailResponse(BaseModel):
    reference: ReferenceResponse
    report: Optional[CredibilityReportResponse]

    class Config:
        from_attributes = True


class RatingCreate(BaseModel):
    rating: int  # 1-5
    comment: Optional[str] = None


class RatingResponse(BaseModel):
    rating_id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True