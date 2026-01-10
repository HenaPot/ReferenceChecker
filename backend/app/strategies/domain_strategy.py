# File: backend/app/strategies/domain_strategy.py

from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import Reference, DomainReputation, DomainCategory
from app.strategies.base_strategy import AnalysisStrategy


class DomainAnalysisStrategy(AnalysisStrategy):
    """
    Analyzes reference credibility based on domain reputation.
    
    Scoring:
    - Academic (.edu, peer-reviewed journals): 30 points
    - Government (.gov): 30 points
    - Established news outlets: 25 points
    - Unknown domains: 10 points
    - Known unreliable sources: 0 points
    """
    
    @property
    def name(self) -> str:
        return "Domain Reputation Analysis"
    
    @property
    def max_score(self) -> int:
        return 30
    
    def analyze(self, reference: Reference) -> Dict[str, Any]:
        """
        Analyze domain reputation and assign score.
        
        Args:
            reference: Reference object with domain populated
            
        Returns:
            Dictionary with score, explanation, and domain info
        """
        if not reference.domain:
            return {
                "score": 0,
                "explanation": "Unable to extract domain from URL",
                "details": {"category": "unknown", "verified": False}
            }
        
        # Query domain reputation database
        domain_rep = self.db.query(DomainReputation).filter(
            DomainReputation.domain_name == reference.domain
        ).first()
        
        if domain_rep:
            # Known domain - use stored score
            score = domain_rep.base_score
            category = domain_rep.category.value
            verified = domain_rep.is_verified
            
            explanation = self._generate_explanation(
                reference.domain, 
                category, 
                score, 
                verified
            )
        else:
            # Unknown domain - apply heuristics
            score, category, explanation = self._analyze_unknown_domain(reference.domain)
            verified = False
        
        return {
            "score": self._clamp_score(score),
            "explanation": explanation,
            "details": {
                "domain": reference.domain,
                "category": category,
                "verified": verified
            }
        }
    
    def _analyze_unknown_domain(self, domain: str) -> tuple[int, str, str]:
        """
        Apply heuristics to unknown domains.
        
        Args:
            domain: Domain name
            
        Returns:
            Tuple of (score, category, explanation)
        """
        domain_lower = domain.lower()
        
        # Check for academic TLD
        if domain_lower.endswith('.edu'):
            return (
                25,  # Slightly lower than verified academic
                "academic",
                f"Domain {domain} uses .edu TLD (educational institution), "
                "but is not in our verified database. Proceeding with caution."
            )
        
        # Check for government TLD
        if domain_lower.endswith('.gov'):
            return (
                25,  # Slightly lower than verified government
                "government",
                f"Domain {domain} uses .gov TLD (government), "
                "but is not in our verified database. Proceeding with caution."
            )
        
        # Check for research/academic keywords
        academic_keywords = ['university', 'academic', 'research', 'scholar', 'institute']
        if any(keyword in domain_lower for keyword in academic_keywords):
            return (
                15,
                "unknown",
                f"Domain {domain} contains academic keywords but is unverified. "
                "Exercise caution when citing this source."
            )
        
        # Default for unknown domains
        return (
            10,
            "unknown",
            f"Domain {domain} is not in our reputation database. "
            "This is an unknown source - verify credibility independently."
        )
    
    def _generate_explanation(
        self, 
        domain: str, 
        category: str, 
        score: int, 
        verified: bool
    ) -> str:
        """
        Generate human-readable explanation for known domains.
        
        Args:
            domain: Domain name
            category: Domain category
            score: Assigned score
            verified: Whether domain is manually verified
            
        Returns:
            Explanation string
        """
        verified_text = "verified" if verified else "catalogued"
        
        explanations = {
            "academic": f"Domain {domain} is a {verified_text} academic/research source. "
                       f"Academic sources typically undergo peer review and maintain high standards. "
                       f"Score: {score}/30",
            
            "government": f"Domain {domain} is a {verified_text} government source. "
                         f"Government sources are generally reliable for official data and policies. "
                         f"Score: {score}/30",
            
            "news": f"Domain {domain} is a {verified_text} news outlet. "
                   f"Established news organizations follow journalistic standards. "
                   f"Score: {score}/30",
            
            "unreliable": f"Domain {domain} is flagged as unreliable in our database. "
                         f"This source has been identified as problematic. "
                         f"Score: {score}/30",
            
            "unknown": f"Domain {domain} is in our database but category is unknown. "
                      f"Score: {score}/30"
        }
        
        return explanations.get(
            category, 
            f"Domain {domain} scored {score}/30 based on our reputation database."
        )