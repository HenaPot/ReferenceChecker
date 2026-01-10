# File: backend/app/strategies/metadata_strategy.py

from typing import Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.models import Reference
from app.strategies.base_strategy import AnalysisStrategy


class MetadataAnalysisStrategy(AnalysisStrategy):
    """
    Analyzes reference credibility based on metadata quality.
    
    Scoring:
    - Has author: +10 points
    - Has publication date: +5 points
    - Published within 2 years: +5 points
    
    Maximum: 20 points
    """
    
    @property
    def name(self) -> str:
        return "Metadata Quality Analysis"
    
    @property
    def max_score(self) -> int:
        return 20
    
    def analyze(self, reference: Reference) -> Dict[str, Any]:
        """
        Analyze metadata completeness and recency.
        
        Args:
            reference: Reference object with metadata fields
            
        Returns:
            Dictionary with score, explanation, and metadata details
        """
        score = 0
        details = {}
        explanations = []
        
        # Check for author (10 points)
        if reference.author and reference.author.strip():
            score += 10
            details["has_author"] = True
            explanations.append(f"✓ Author identified: {reference.author}")
        else:
            details["has_author"] = False
            explanations.append("✗ No author information available (-10 points)")
        
        # Check for publication date (5 points)
        if reference.publication_date:
            score += 5
            details["has_date"] = True
            details["publication_date"] = reference.publication_date.isoformat()
            
            # Check recency (5 points for publications within 2 years)
            age_score, age_explanation = self._analyze_recency(reference.publication_date)
            score += age_score
            details["recency_score"] = age_score
            details["age_days"] = (date.today() - reference.publication_date).days
            
            explanations.append(f"✓ Publication date: {reference.publication_date}")
            explanations.append(age_explanation)
        else:
            details["has_date"] = False
            details["recency_score"] = 0
            explanations.append("✗ No publication date available (-10 points)")
        
        # Generate overall explanation
        explanation = self._generate_explanation(score, explanations)
        
        return {
            "score": self._clamp_score(score),
            "explanation": explanation,
            "details": details
        }
    
    def _analyze_recency(self, pub_date: date) -> tuple[int, str]:
        """
        Analyze how recent the publication is.
        
        Args:
            pub_date: Publication date
            
        Returns:
            Tuple of (score, explanation)
        """
        today = date.today()
        age = today - pub_date
        years_old = age.days / 365.25
        
        if years_old < 0:
            # Future date - suspicious
            return (0, "⚠ Publication date is in the future (suspicious, 0 points)")
        elif years_old <= 2:
            # Very recent
            return (5, f"✓ Recent publication ({years_old:.1f} years old, +5 points)")
        elif years_old <= 5:
            # Moderately recent
            return (3, f"○ Moderately recent ({years_old:.1f} years old, +3 points)")
        elif years_old <= 10:
            # Older but still relevant
            return (1, f"○ Older publication ({years_old:.1f} years old, +1 point)")
        else:
            # Very old
            return (0, f"✗ Very old publication ({years_old:.1f} years old, 0 points)")
    
    def _generate_explanation(self, score: int, explanations: list[str]) -> str:
        """
        Generate comprehensive explanation from individual checks.
        
        Args:
            score: Total metadata score
            explanations: List of individual check explanations
            
        Returns:
            Combined explanation string
        """
        intro = f"Metadata quality score: {score}/20. "
        
        if score >= 18:
            quality = "Excellent metadata completeness."
        elif score >= 15:
            quality = "Good metadata quality."
        elif score >= 10:
            quality = "Adequate metadata, but some information missing."
        elif score >= 5:
            quality = "Poor metadata quality - significant information missing."
        else:
            quality = "Very poor metadata - critical information absent."
        
        return intro + quality + " " + " ".join(explanations)