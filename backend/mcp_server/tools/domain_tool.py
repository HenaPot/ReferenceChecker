# File: backend/mcp_server/tools/domain_tool.py

import os
import sys
from typing import Dict, Any

# Add parent directory to path to import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import DomainReputation
from app.config import settings


# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


async def get_domain_reputation(domain: str) -> Dict[str, Any]:
    """
    Look up domain reputation in the database.
    
    Args:
        domain: Domain name (e.g., 'nature.com')
        
    Returns:
        Dictionary with domain reputation info
    """
    db = SessionLocal()
    
    try:
        # Query domain reputation
        domain_rep = db.query(DomainReputation).filter(
            DomainReputation.domain_name == domain
        ).first()
        
        if domain_rep:
            # Known domain
            return {
                "domain": domain,
                "score": domain_rep.base_score,
                "max_score": 30,
                "category": domain_rep.category.value,
                "verified": domain_rep.is_verified,
                "explanation": f"Domain {domain} is a {'verified' if domain_rep.is_verified else 'catalogued'} {domain_rep.category.value} source. Score: {domain_rep.base_score}/30"
            }
        else:
            # Unknown domain - apply heuristics
            score, category = _analyze_unknown_domain(domain)
            
            return {
                "domain": domain,
                "score": score,
                "max_score": 30,
                "category": category,
                "verified": False,
                "explanation": f"Domain {domain} is not in our database. {_get_category_explanation(category, domain)}. Score: {score}/30"
            }
    
    finally:
        db.close()


def _analyze_unknown_domain(domain: str) -> tuple[int, str]:
    """Apply heuristics to unknown domains."""
    domain_lower = domain.lower()
    
    # Check for academic TLD
    if domain_lower.endswith('.edu'):
        return 25, "academic"
    
    # Check for government TLD
    if domain_lower.endswith('.gov'):
        return 25, "government"
    
    # Check for research/academic keywords
    academic_keywords = ['university', 'academic', 'research', 'scholar', 'institute']
    if any(keyword in domain_lower for keyword in academic_keywords):
        return 15, "academic"
    
    # Default for unknown domains
    return 10, "unknown"


def _get_category_explanation(category: str, domain: str) -> str:
    """Get explanation based on category."""
    explanations = {
        "academic": f"Uses .edu TLD or academic keywords",
        "government": f"Uses .gov TLD",
        "unknown": f"Unknown source - verify credibility independently"
    }
    
    return explanations.get(category, "Category not recognized")