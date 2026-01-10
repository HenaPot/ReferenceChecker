# File: backend/app/api/references.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import User, Reference, ReferenceStatus
from app.schemas.reference import ReferenceCreate, ReferenceResponse, ReferenceDetailResponse
from app.utils.security import get_current_user
from app.services.reference_service import ReferenceService

router = APIRouter()


@router.post("/check", response_model=ReferenceResponse, status_code=status.HTTP_201_CREATED)
async def check_reference(
    reference_data: ReferenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a reference for credibility checking.
    Returns immediately with status 'processing'.
    """
    service = ReferenceService(db)
    reference = await service.create_reference(reference_data.url, current_user.user_id)
    
    # TODO: Trigger async processing (N8N webhook, background task, etc.)
    
    return reference


@router.get("/history", response_model=List[ReferenceResponse])
async def get_reference_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's reference checking history with pagination."""
    references = (
        db.query(Reference)
        .filter(Reference.user_id == current_user.user_id)
        .order_by(Reference.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return references


@router.get("/{reference_id}", response_model=ReferenceDetailResponse)
async def get_reference_detail(
    reference_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific reference."""
    reference = db.query(Reference).filter(
        Reference.reference_id == reference_id,
        Reference.user_id == current_user.user_id
    ).first()
    
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found"
        )
    
    return {
        "reference": reference,
        "report": reference.credibility_report
    }


@router.delete("/{reference_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reference(
    reference_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a reference from history."""
    reference = db.query(Reference).filter(
        Reference.reference_id == reference_id,
        Reference.user_id == current_user.user_id
    ).first()
    
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found"
        )
    
    db.delete(reference)
    db.commit()
    
    return None