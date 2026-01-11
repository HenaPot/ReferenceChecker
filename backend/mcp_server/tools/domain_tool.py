# File: backend/mcp_server/tools/domain_tool.py

import os
import sys
from typing import Dict, Any

# Add parent directory to path to import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.strategies.domain_strategy import DomainAnalysisStrategy
from app.config import settings


# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


async def get_domain_reputation(domain: str) -> Dict[str, Any]:
    """
    Look up domain reputation using the DomainAnalysisStrategy.
    
    This delegates to the existing strategy instead of duplicating logic.
    
    Args:
        domain: Domain name (e.g., 'nature.com')
        
    Returns:
        Dictionary with domain reputation info
    """
    db = SessionLocal()
    
    try:
        # Create a minimal Reference object for the strategy
        # We only need the domain field populated
        from app.models import Reference
        temp_reference = Reference(domain=domain)
        
        # Use the existing strategy
        strategy = DomainAnalysisStrategy(db)
        result = strategy.analyze(temp_reference)
        
        # Convert to MCP-compatible format
        return {
            "domain": domain,
            "score": result["score"],
            "max_score": strategy.max_score,
            "verified": result.get("details", {}).get("verified", False),
            "category": result.get("details", {}).get("category", "unknown"),
            "explanation": result["explanation"]
        }
    
    finally:
        db.close()