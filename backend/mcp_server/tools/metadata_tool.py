# File: backend/mcp_server/tools/metadata_tool.py

from typing import Dict, Any, Optional
from datetime import datetime, date


async def analyze_metadata(
    title: Optional[str] = None,
    author: Optional[str] = None,
    publication_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze metadata quality for a reference.
    
    Args:
        title: Article/paper title
        author: Author name(s)
        publication_date: Publication date (YYYY-MM-DD format)
        
    Returns:
        Dictionary with metadata analysis
    """
    score = 0
    max_score = 20
    details = []
    
    # Check for author (10 points)
    if author and author.strip():
        score += 10
        details.append(f"✓ Author identified: {author}")
    else:
        details.append("✗ No author information (-10 points)")
    
    # Check for publication date (5 points)
    if publication_date:
        try:
            pub_date = datetime.fromisoformat(publication_date).date()
            score += 5
            details.append(f"✓ Publication date: {pub_date}")
            
            # Check recency (5 points)
            age_days = (date.today() - pub_date).days
            years_old = age_days / 365.25
            
            if years_old < 0:
                details.append("⚠ Publication date is in the future (suspicious)")
            elif years_old <= 2:
                score += 5
                details.append(f"✓ Recent publication ({years_old:.1f} years old, +5 points)")
            elif years_old <= 5:
                score += 3
                details.append(f"○ Moderately recent ({years_old:.1f} years old, +3 points)")
            elif years_old <= 10:
                score += 1
                details.append(f"○ Older publication ({years_old:.1f} years old, +1 point)")
            else:
                details.append(f"✗ Very old publication ({years_old:.1f} years old, 0 points)")
        
        except (ValueError, TypeError):
            details.append("⚠ Invalid publication date format")
    else:
        details.append("✗ No publication date (-10 points)")
    
    # Check for title (informational only, not scored)
    if title and title.strip():
        details.append(f"✓ Title present: {title[:50]}...")
    else:
        details.append("○ No title provided")
    
    return {
        "score": score,
        "max_score": max_score,
        "has_author": bool(author and author.strip()),
        "has_date": bool(publication_date),
        "has_title": bool(title and title.strip()),
        "explanation": f"Metadata quality: {score}/{max_score}. " + " ".join(details)
    }