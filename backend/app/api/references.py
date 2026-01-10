# File: backend/app/api/references.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import User, Reference
from app.models.reference import ReferenceStatus
from app.schemas.reference import ReferenceCreate, ReferenceResponse, ReferenceDetailResponse
from app.utils.security import get_current_user
from app.services.reference_service import ReferenceService
from app.services.credibility_analyzer import CredibilityAnalyzer

router = APIRouter()

async def run_credibility_analysis(reference_id: UUID, db: Session):
    """
    Background task to run credibility analysis on a reference.
    
    Args:
        reference_id: UUID of reference to analyze
        db: Database session
    """
    try:
        # Get reference
        reference = db.query(Reference).filter(
            Reference.reference_id == reference_id
        ).first()
        
        if not reference:
            return
        
        # Run credibility analysis
        analyzer = CredibilityAnalyzer(db)
        await analyzer.analyze_reference(reference)
        
    except Exception as e:
        # If analysis fails, update reference status
        reference = db.query(Reference).filter(
            Reference.reference_id == reference_id
        ).first()
        
        if reference:
            # FIXED: Use the correct enum value
            reference.status = ReferenceStatus.failed
            db.commit()
        
        # Log error (you can add proper logging here)
        print(f"Credibility analysis failed for {reference_id}: {str(e)}")
        import traceback
        traceback.print_exc()


@router.post("/check", response_model=ReferenceResponse, status_code=status.HTTP_201_CREATED)
async def check_reference(
    reference_data: ReferenceCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a reference for credibility checking.
    Returns immediately with status 'processing'.
    """
    service = ReferenceService(db)
    reference = await service.create_reference(reference_data.url, current_user.user_id)
    
    background_tasks.add_task(
        run_credibility_analysis,
        reference.reference_id,
        db
    )
    
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


@router.post("/{reference_id}/reanalyze", response_model=ReferenceResponse)
async def reanalyze_reference(
    reference_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger re-analysis of a reference.
    Useful if the original analysis failed or you want updated results.
    """
    reference = db.query(Reference).filter(
        Reference.reference_id == reference_id,
        Reference.user_id == current_user.user_id
    ).first()
    
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found"
        )
    
    reference.status = ReferenceStatus.processing
    db.commit()
    
    # Trigger background analysis
    background_tasks.add_task(
        run_credibility_analysis,
        reference.reference_id,
        db
    )
    
    db.refresh(reference)
    return reference


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