# File: backend/mcp_server/tools/check_reference_tool.py

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.credibility_analyzer import CredibilityAnalyzer
from app.services.reference_service import ReferenceService
from app.services.scraper_service import WebScraperService
from app.config import settings


# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


async def check_reference(
    url: str,
    title: Optional[str] = None,
    author: Optional[str] = None,
    publication_date: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Perform full credibility analysis using CredibilityAnalyzer.
    
    Args:
        url: URL to check
        title: Optional title
        author: Optional author
        publication_date: Optional publication date (YYYY-MM-DD)
        user_id: Optional user ID (uses system user if not provided)
        
    Returns:
        Complete credibility analysis
    """
    db = SessionLocal()
    
    try:
        # Create or use user ID
        if not user_id:
            # For MCP calls without authentication, use a system user ID
            user_id = UUID('00000000-0000-0000-0000-000000000000')
        
        # 1. Create reference
        ref_service = ReferenceService(db)
        reference = await ref_service.create_reference(url, user_id)
        
        # 2. Scrape metadata if not provided
        if not (title and author and publication_date):
            try:
                scraper = WebScraperService()
                scraped = scraper.scrape_metadata(url)  # SYNC method
                
                # Use scraped data as fallback
                title = title or scraped.get('title')
                author = author or scraped.get('author')
                publication_date = publication_date or scraped.get('publication_date')
            except Exception as e:
                print(f"Warning: Web scraping failed: {e}")
        
        # 3. Update reference with metadata
        if title or author or publication_date:
            pub_date_obj = None
            if publication_date:
                try:
                    pub_date_obj = datetime.fromisoformat(publication_date).date()
                except (ValueError, TypeError):
                    pass
            
            reference = ref_service.update_reference_metadata(
                reference.reference_id,
                title=title,
                author=author,
                publication_date=pub_date_obj
            )
        
        # 4. Analyze with CredibilityAnalyzer
        analyzer = CredibilityAnalyzer(db)
        report = await analyzer.analyze_reference(reference)
        
        # 5. Format and return response
        return {
            "url": url,
            "reference_id": str(reference.reference_id),
            "domain": reference.domain,
            "title": reference.title,
            "author": reference.author,
            "publication_date": reference.publication_date.isoformat() if reference.publication_date else None,
            "credibility_analysis": {
                "total_score": report.total_score,
                "max_score": 100,
                "credibility_level": _get_credibility_level(report.total_score),
                "breakdown": {
                    "domain": {
                        "score": report.domain_score,
                        "max_score": 30,
                        "explanation": report.domain_explanation
                    },
                    "metadata": {
                        "score": report.metadata_score,
                        "max_score": 20,
                        "explanation": report.metadata_explanation
                    },
                    "rag": {
                        "score": report.rag_score,
                        "max_score": 25,
                        "explanation": report.rag_explanation
                    },
                    "ai": {
                        "score": report.ai_score,
                        "max_score": 25,
                        "explanation": report.ai_explanation
                    }
                },
                "red_flags": report.red_flags
            },
            "analyzed_at": report.created_at.isoformat()
        }
    
    finally:
        db.close()


def _get_credibility_level(score: int) -> str:
    """Determine credibility level based on score."""
    if score >= 80:
        return "highly_credible"
    elif score >= 60:
        return "credible"
    elif score >= 40:
        return "questionable"
    elif score >= 20:
        return "unreliable"
    else:
        return "highly_unreliable"