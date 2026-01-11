# File: backend/app/strategies/rag_strategy.py

from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import Reference
from app.strategies.base_strategy import AnalysisStrategy
from app.services.rag_service import RAGService


class RAGAnalysisStrategy(AnalysisStrategy):
    """
    Analyzes reference credibility based on cross-reference support from RAG database.
    
    Scoring:
    - 5+ similar credible sources with high similarity: 25 points
    - 3-4 similar sources: 20 points
    - 2 similar sources: 15 points
    - 1 similar source: 10 points
    - 0 similar sources: 5 points (default minimum)
    
    Maximum: 25 points
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.rag_service = RAGService(db)
    
    @property
    def name(self) -> str:
        return "Cross-Reference Analysis (RAG)"
    
    @property
    def max_score(self) -> int:
        return 25
    
    def analyze(self, reference: Reference) -> Dict[str, Any]:
        """
        Analyze cross-reference support using RAG vector similarity search.
        
        Args:
            reference: Reference object to analyze
            
        Returns:
            Dictionary with score, explanation, and similar sources
        """
        # Prepare text for similarity search
        query_text = self._prepare_query_text(reference)
        
        if not query_text:
            return {
                "score": 5,
                "explanation": "Insufficient information to perform cross-reference analysis. "
                              "Default score of 5/25 assigned.",
                "details": {
                    "similar_sources": [],
                    "count": 0,
                    "has_corroboration": False
                }
            }
        
        # Find similar sources
        try:
            analysis = self.rag_service.analyze_cross_references(query_text, top_k=5)
            similar_sources = analysis["similar_sources"]
            count = analysis["count"]
            avg_similarity = analysis["average_similarity"]
            
            # Calculate score based on number and quality of similar sources
            score = self._calculate_score(count, avg_similarity)
            
            # Generate explanation
            explanation = self._generate_explanation(
                count, 
                avg_similarity, 
                score,
                similar_sources
            )
            
            return {
                "score": self._clamp_score(score),
                "explanation": explanation,
                "details": {
                    "similar_sources": similar_sources,
                    "count": count,
                    "average_similarity": avg_similarity,
                    "has_corroboration": analysis["has_corroboration"]
                }
            }
        
        except Exception as e:
            self.db.rollback()
            
            # If RAG search fails, return default score
            return {
                "score": 5,
                "explanation": f"Cross-reference analysis encountered an error. "
                              f"Default score of 5/25 assigned. Error: {str(e)}",
                "details": {
                    "similar_sources": [],
                    "count": 0,
                    "has_corroboration": False,
                    "error": str(e)
                }
            }
    
    def _prepare_query_text(self, reference: Reference) -> str:
        parts = []

        if reference.title:
            parts.append(reference.title)

        # If your Reference model has any summary/description field, use it
        if hasattr(reference, "abstract") and reference.abstract:
            parts.append(reference.abstract)

        # Fallback: if no abstract, use URL-derived hints
        if len(parts) == 1 and reference.url:
            slug = reference.url.split("/")[-1]
            slug = slug.replace("-", " ").replace("_", " ")
            parts.append(slug)

        return ". ".join(parts)
        """
        Prepare text for RAG similarity search.
        
        Args:
            reference: Reference object
            
        Returns:
            Combined text for search, or empty string if insufficient info
        """
        parts = []
        
        if reference.title:
            parts.append(reference.title)
        
        if reference.author:
            parts.append(f"by {reference.author}")
        
        # If we have very little info, use URL as fallback
        if not parts and reference.url:
            # Extract some info from URL (domain, path keywords)
            parts.append(reference.url.split('/')[-1].replace('-', ' ').replace('_', ' '))
        
        return ". ".join(parts)
    
    def _calculate_score(self, count: int, avg_similarity: float) -> int:
        """
        Calculate RAG score based on similar sources found.
        
        Args:
            count: Number of similar sources
            avg_similarity: Average similarity score
            
        Returns:
            Score from 5 to 25
        """
        # Base score on count
        if count >= 5:
            base_score = 25
        elif count == 4:
            base_score = 20
        elif count == 3:
            base_score = 17
        elif count == 2:
            base_score = 13
        elif count == 1:
            base_score = 8
        else:
            base_score = 5
        
        # Adjust based on average similarity quality
        if avg_similarity < 0.5:
            # Low similarity - reduce score
            base_score = int(base_score * 0.7)
        elif avg_similarity >= 0.8:
            # Very high similarity - keep full score
            pass
        elif avg_similarity >= 0.6:
            # Good similarity - slight reduction
            base_score = int(base_score * 0.9)
        else:
            # Moderate similarity
            base_score = int(base_score * 0.8)
        
        return base_score
    
    def _generate_explanation(
        self, 
        count: int, 
        avg_similarity: float,
        score: int,
        similar_sources: list
    ) -> str:
        """
        Generate human-readable explanation.
        
        Args:
            count: Number of similar sources
            avg_similarity: Average similarity
            score: Calculated score
            similar_sources: List of similar sources
            
        Returns:
            Explanation string
        """
        if count == 0:
            return (
                f"No similar sources found in our database of credible references. "
                f"This could indicate novel research or a topic not well-covered in our database. "
                f"Score: {score}/25"
            )
        
        # Build source list
        top_sources = similar_sources[:3]  # Show top 3
        source_list = ", ".join([
            f"{s['title'][:50]}... (similarity: {s['similarity']:.2f})"
            for s in top_sources
        ])
        
        quality_desc = ""
        if avg_similarity >= 0.8:
            quality_desc = "very high similarity"
        elif avg_similarity >= 0.6:
            quality_desc = "good similarity"
        elif avg_similarity >= 0.5:
            quality_desc = "moderate similarity"
        else:
            quality_desc = "low similarity"
        
        return (
            f"Found {count} similar source(s) in our database with {quality_desc} "
            f"(avg: {avg_similarity:.2f}). "
            f"Top matches: {source_list}. "
            f"Cross-reference support score: {score}/25"
        )