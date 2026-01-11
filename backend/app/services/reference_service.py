# File: backend/app/services/reference_service.py

from sqlalchemy.orm import Session
from urllib.parse import urlparse
from uuid import UUID
from datetime import datetime

from app.models import Reference, ReferenceStatus
from app.services.scraper_service import WebScraperService


class ReferenceService:
    """Service for managing references."""
    
    def __init__(self, db: Session):
        self.db = db
        self.scraper = WebScraperService()
    
    async def create_reference(self, url: str, user_id: UUID) -> Reference:
        """
        Create a new reference for analysis.
        Extracts domain and scrapes metadata (title, author, date).
        """
        # Extract domain from URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")
        
        # Scrape metadata from URL (run in thread pool to avoid blocking)
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            metadata = await loop.run_in_executor(None, self.scraper.scrape_metadata, url)
        except Exception as e:
            print(f"Scraping failed for {url}: {str(e)}")
            metadata = {'title': None, 'author': None, 'publication_date': None}
        
        # Parse publication date
        pub_date = None
        if metadata.get('publication_date'):
            try:
                pub_date = datetime.strptime(metadata['publication_date'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Create reference with scraped metadata
        reference = Reference(
            user_id=user_id,
            url=url,
            domain=domain,
            title=metadata.get('title'),
            author=metadata.get('author'),
            publication_date=pub_date,
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