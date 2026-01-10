# File: backend/mcp_server/tools/rag_tool.py

import os
import sys
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
from app.models import RAGSource
from app.config import settings
import json


# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Lazy-load embedding model
_embedding_model = None


def get_embedding_model():
    """Lazy-load the embedding model."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedding_model


async def search_similar_sources(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Search for similar sources in the RAG database.
    
    Args:
        query: Search query text
        top_k: Number of results to return
        
    Returns:
        Dictionary with similar sources and analysis
    """
    db = SessionLocal()
    
    try:
        # Generate query embedding
        model = get_embedding_model()
        query_embedding = model.encode(query).tolist()
        
        # Get all sources with embeddings
        all_sources = db.query(RAGSource).filter(
            RAGSource.embedding_vector.isnot(None)
        ).all()
        
        if not all_sources:
            return {
                "score": 5,
                "max_score": 25,
                "similar_sources": [],
                "count": 0,
                "explanation": "No sources found in RAG database."
            }
        
        # Calculate similarities
        similarities = []
        for source in all_sources:
            try:
                stored_embedding = json.loads(source.embedding_vector)
                similarity = _cosine_similarity(query_embedding, stored_embedding)
                
                similarities.append({
                    "source_id": str(source.source_id),
                    "url": source.url,
                    "title": source.title,
                    "domain": source.domain,
                    "credibility_score": source.credibility_score,
                    "similarity": round(similarity, 3),
                    "content_preview": source.content_text[:150] + "..." if source.content_text else None
                })
            except (json.JSONDecodeError, TypeError):
                continue
        
        # Sort by similarity and get top_k
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        top_sources = similarities[:top_k]
        
        # Filter by minimum similarity threshold
        min_similarity = 0.3
        filtered_sources = [s for s in top_sources if s["similarity"] >= min_similarity]
        
        # Calculate score based on results
        if not filtered_sources:
            score = 5
            explanation = "No similar sources found above similarity threshold."
        else:
            avg_similarity = sum(s["similarity"] for s in filtered_sources) / len(filtered_sources)
            
            # Score based on count and quality
            if len(filtered_sources) >= 5 and avg_similarity >= 0.6:
                score = 25
            elif len(filtered_sources) >= 3 and avg_similarity >= 0.5:
                score = 20
            elif len(filtered_sources) >= 2:
                score = 15
            elif len(filtered_sources) >= 1:
                score = 10
            else:
                score = 5
            
            explanation = (
                f"Found {len(filtered_sources)} similar source(s) with "
                f"average similarity {avg_similarity:.2f}. Top matches: "
                f"{', '.join([s['title'][:30] + '...' for s in filtered_sources[:3]])}"
            )
        
        return {
            "score": score,
            "max_score": 25,
            "similar_sources": filtered_sources,
            "count": len(filtered_sources),
            "average_similarity": round(sum(s["similarity"] for s in filtered_sources) / len(filtered_sources), 3) if filtered_sources else 0,
            "explanation": explanation
        }
    
    finally:
        db.close()


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return max(0.0, min(1.0, dot_product / (magnitude1 * magnitude2)))