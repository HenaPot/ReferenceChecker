# File: backend/mcp_server/tools/rag_tool.py

import os
import sys
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.strategies.rag_strategy import RAGAnalysisStrategy
from app.config import settings


# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


async def search_similar_sources(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Search for similar sources using the RAGAnalysisStrategy.
    
    This delegates to the existing strategy instead of duplicating logic.
    
    Args:
        query: Search query text
        top_k: Number of results to return (default: 5)
        
    Returns:
        Dictionary with similar sources and analysis
    """
    db = SessionLocal()
    
    try:
        # Create a minimal Reference object with just the query as title
        from app.models import Reference
        temp_reference = Reference(title=query)
        
        # Use the existing strategy
        strategy = RAGAnalysisStrategy(db)
        result = strategy.analyze(temp_reference)
        
        # Extract details
        details = result.get("details", {})
        similar_sources = details.get("similar_sources", [])
        
        # Convert to MCP-compatible format
        return {
            "score": result["score"],
            "max_score": strategy.max_score,
            "similar_sources": similar_sources[:top_k],  # Limit to top_k
            "count": details.get("count", 0),
            "average_similarity": details.get("average_similarity", 0.0),
            "explanation": result["explanation"]
        }
    
    finally:
        db.close()