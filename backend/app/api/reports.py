# File: backend/app/api/reports.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import User, Reference, CredibilityReport
from app.schemas.reference import CredibilityReportResponse
from app.utils.security import get_current_user

router = APIRouter()


@router.get("/{reference_id}", response_model=CredibilityReportResponse)
async def get_credibility_report(
    reference_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get credibility report for a reference."""
    
    # Verify reference belongs to user
    reference = db.query(Reference).filter(
        Reference.reference_id == reference_id,
        Reference.user_id == current_user.user_id
    ).first()
    
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found"
        )
    
    if not reference.credibility_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credibility report not yet generated"
        )
    
    return reference.credibility_report