# File: backend/app/services/reference_service.py

from sqlalchemy.orm import Session
from urllib.parse import urlparse
from uuid import UUID

from app.models import Reference, ReferenceStatus


class ReferenceService:
    """Service for managing references."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_reference(self, url: str, user_id: UUID) -> Reference:
        """
        Create a new reference for analysis.
        Extracts basic info (domain) and sets status to 'processing'.
        """
        # Extract domain from URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")
        
        # Create reference
        reference = Reference(
            user_id=user_id,
            url=url,
            domain=domain,
            status=ReferenceStatus.processing
        )
        
        self.db.add(reference)
        self.db.commit()
        self.db.refresh(reference)
        
        return reference
    
    def get_reference(self, reference_id: UUID) -> Reference:
        """Get a reference by ID."""
        return self.db.query(Reference).filter(
            Reference.reference_id == reference_id
        ).first()
    
    def update_reference_metadata(
        self,
        reference_id: UUID,
        title: str = None,
        author: str = None,
        publication_date = None
    ) -> Reference:
        """Update reference metadata."""
        reference = self.get_reference(reference_id)
        
        if not reference:
            return None
        
        if title:
            reference.title = title
        if author:
            reference.author = author
        if publication_date:
            reference.publication_date = publication_date
        
        self.db.commit()
        self.db.refresh(reference)
        
        return reference