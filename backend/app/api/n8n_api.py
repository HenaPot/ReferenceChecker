# File: backend/app/api/n8n.py
# NEW FILE - API endpoint for N8N to send enriched data back

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID

from app.database import get_db
from app.models import Reference

router = APIRouter()


class EnrichmentData(BaseModel):
    """Schema for enriched data from N8N"""
    reference_id: str
    url: str
    title: Optional[str] = None
    credibility_score: int
    enrichment: Dict[str, Any]
    enriched_at: str


@router.post("/enrichment")
async def receive_enrichment(
    data: EnrichmentData,
    db: Session = Depends(get_db)
):
    """
    Receive enriched reference data from N8N workflow.
    
    This endpoint is called by N8N after it enriches the reference
    with external data (citations, academic metadata, etc.)
    """
    try:
        # Find the reference
        reference_id = UUID(data.reference_id)
        reference = db.query(Reference).filter(
            Reference.reference_id == reference_id
        ).first()
        
        if not reference:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reference not found"
            )
        
        # Store enrichment data (you can add a JSON field to Reference model)
        # For now, we'll just log it
        print(f"✅ Received enrichment for {reference.url}:")
        print(f"   - Citations found: {data.enrichment.get('citations_found', 0)}")
        print(f"   - Citation count: {data.enrichment.get('citation_count', 0)}")
        print(f"   - DOI: {data.enrichment.get('doi', 'N/A')}")
        
        # TODO: Store in database (add enrichment_data JSON field to Reference model)
        # reference.enrichment_data = data.enrichment
        # db.commit()
        
        return {
            "success": True,
            "message": "Enrichment data received",
            "reference_id": str(reference_id)
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reference_id format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing enrichment: {str(e)}"
        )
