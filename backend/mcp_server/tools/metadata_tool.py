# File: backend/mcp_server/tools/metadata_tool.py

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.strategies.metadata_strategy import MetadataAnalysisStrategy
from app.config import settings


# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


async def analyze_metadata(
    title: Optional[str] = None,
    author: Optional[str] = None,
    publication_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze metadata quality using the MetadataAnalysisStrategy.
    
    This delegates to the existing strategy instead of duplicating logic.
    
    Args:
        title: Article/paper title
        author: Author name(s)
        publication_date: Publication date (YYYY-MM-DD format)
        
    Returns:
        Dictionary with metadata analysis
    """
    db = SessionLocal()
    
    try:
        # Create a minimal Reference object for the strategy
        from app.models import Reference
        
        # Convert string date to date object if provided
        pub_date_obj = None
        if publication_date:
            try:
                pub_date_obj = datetime.fromisoformat(publication_date).date()
            except (ValueError, TypeError):
                pass  # Let strategy handle invalid dates
        
        temp_reference = Reference(
            title=title,
            author=author,
            publication_date=pub_date_obj
        )
        
        # Use the existing strategy
        strategy = MetadataAnalysisStrategy(db)
        result = strategy.analyze(temp_reference)
        
        # Convert to MCP-compatible format
        return {
            "score": result["score"],
            "max_score": strategy.max_score,
            "has_author": bool(author and author.strip()),
            "has_date": bool(publication_date),
            "has_title": bool(title and title.strip()),
            "explanation": result["explanation"]
        }
    
    finally:
        db.close()