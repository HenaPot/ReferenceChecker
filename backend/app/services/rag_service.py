# File: backend/app/services/rag_service.py

from typing import List, Dict, Any
import json
from sqlalchemy.orm import Session
from sqlalchemy import text
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from app.models import RAGSource
from app.config import settings


class RAGService:
    """
    Service for Retrieval-Augmented Generation (RAG) using vector similarity search.
    
    Uses sentence-transformers for embeddings and PostgreSQL with pgvector
    for similarity search.
    """
    
    def __init__(self, db: Session):
        """
        Initialize RAG service with database session and embedding model.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self._model = None
    
    @property
    def model(self) -> SentenceTransformer:
        """
        Lazy-load the embedding model (only load when needed).
        
        Returns:
            SentenceTransformer model
        """
        if self._model is None:
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self._model
    
    def find_similar_sources(
        self, 
        query_text: str, 
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find sources similar to the query text using vector similarity.
        
        Args:
            query_text: Text to search for similar sources
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold (0-1)
            
        Returns:
            List of dictionaries containing similar sources with similarity scores
        """
        # Generate embedding for query
        query_embedding = self.model.encode(query_text).tolist()

        stmt = (
            select(
                RAGSource.source_id,
                RAGSource.url,
                RAGSource.title,
                RAGSource.content_text,
                RAGSource.domain,
                RAGSource.credibility_score,
                (1 - RAGSource.embedding_vector.cosine_distance(query_embedding)).label("similarity"),
            )
            .where(RAGSource.embedding_vector.isnot(None))
            .order_by(RAGSource.embedding_vector.cosine_distance(query_embedding))
            .limit(top_k)
        )

        rows = self.db.execute(stmt).all()

        similar_sources = []
        for row in rows:
            if row.similarity >= min_similarity:
                similar_sources.append({
                    "source_id": str(row.source_id),
                    "url": row.url,
                    "title": row.title,
                    "content_text": row.content_text[:200] + "..." if row.content_text else None,
                    "domain": row.domain,
                    "credibility_score": row.credibility_score,
                    "similarity": round(float(row.similarity), 3),
                })

        return similar_sources

    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score between 0 and 1
        """
        # Ensure same length
        if len(vec1) != len(vec2):
            return 0.0
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Calculate magnitudes
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        # Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        # Cosine similarity
        similarity = dot_product / (magnitude1 * magnitude2)
        
        # Clamp to [0, 1] range
        return max(0.0, min(1.0, similarity))
    
    def analyze_cross_references(
        self, 
        reference_text: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze cross-references for a given reference text.
        
        Args:
            reference_text: Text to analyze (title + abstract)
            top_k: Number of similar sources to find
            
        Returns:
            Dictionary with similar sources and analysis
        """
        similar_sources = self.find_similar_sources(reference_text, top_k=top_k)
        
        if not similar_sources:
            return {
                "similar_sources": [],
                "count": 0,
                "average_similarity": 0.0,
                "has_corroboration": False
            }
        
        avg_similarity = sum(s["similarity"] for s in similar_sources) / len(similar_sources)
        
        return {
            "similar_sources": similar_sources,
            "count": len(similar_sources),
            "average_similarity": round(avg_similarity, 3),
            "has_corroboration": len(similar_sources) >= 3 and avg_similarity >= 0.6
        }