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
from app.services.n8n_service import N8NService

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
        report = await analyzer.analyze_reference(reference)
        
        try:
            n8n_service = N8NService()
            await n8n_service.send_reference_analyzed(
                reference_id=str(reference.reference_id),
                url=reference.url,
                title=reference.title,
                author=reference.author,
                domain=reference.domain,
                credibility_score=report.total_score,
                breakdown={
                    "domain_score": report.domain_score,
                    "metadata_score": report.metadata_score,
                    "rag_score": report.rag_score,
                    "ai_score": report.ai_score
                }
            )
        except Exception as n8n_error:
            # Don't fail analysis if N8N webhook fails
            print(f"⚠️  N8N webhook failed (analysis still succeeded): {n8n_error}")
        
    except Exception as e:
        # If analysis fails, update reference status
        reference = db.query(Reference).filter(
            Reference.reference_id == reference_id
        ).first()
        
        if reference:
            reference.status = ReferenceStatus.failed
            db.commit()
        
        # Log error
        print(f"❌ Credibility analysis failed for {reference_id}: {str(e)}")
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
    Analysis happens in background + sends to N8N.
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