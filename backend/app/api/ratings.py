# File: backend/app/api/ratings.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID

from app.database import get_db
from app.models import User, Reference, UserRating
from app.schemas.reference import RatingCreate, RatingResponse
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/{reference_id}", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def create_rating(
    reference_id: UUID,
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a rating for a reference."""
    
    # Validate rating value
    if not (1 <= rating_data.rating <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # Check if reference exists
    reference = db.query(Reference).filter(Reference.reference_id == reference_id).first()
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found"
        )
    
    # Check if user already rated this reference
    existing_rating = db.query(UserRating).filter(
        UserRating.user_id == current_user.user_id,
        UserRating.reference_id == reference_id
    ).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating_data.rating
        existing_rating.comment = rating_data.comment
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    
    # Create new rating
    new_rating = UserRating(
        user_id=current_user.user_id,
        reference_id=reference_id,
        rating=rating_data.rating,
        comment=rating_data.comment
    )
    
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    
    return new_rating


@router.get("/{reference_id}/aggregate")
async def get_aggregate_rating(
    reference_id: UUID,
    db: Session = Depends(get_db)
):
    """Get aggregate rating statistics for a reference."""
    
    # Check if reference exists
    reference = db.query(Reference).filter(Reference.reference_id == reference_id).first()
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found"
        )
    
    # Calculate aggregate statistics
    ratings = db.query(UserRating).filter(UserRating.reference_id == reference_id).all()
    
    if not ratings:
        return {
            "reference_id": reference_id,
            "average_rating": None,
            "total_ratings": 0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
    
    # Calculate average
    avg_rating = sum(r.rating for r in ratings) / len(ratings)
    
    # Calculate distribution
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating in ratings:
        distribution[rating.rating] += 1
    
    return {
        "reference_id": reference_id,
        "average_rating": round(avg_rating, 2),
        "total_ratings": len(ratings),
        "rating_distribution": distribution
    }