# File: backend/app/strategies/base_strategy.py

from abc import ABC, abstractmethod
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import Reference


class AnalysisStrategy(ABC):
    """
    Abstract base class for credibility analysis strategies.
    
    Each strategy analyzes one aspect of a reference's credibility
    and returns a score with explanation.
    """
    
    def __init__(self, db: Session):
        """
        Initialize strategy with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name for logging and debugging."""
        pass
    
    @property
    @abstractmethod
    def max_score(self) -> int:
        """Maximum possible score this strategy can return."""
        pass
    
    @abstractmethod
    def analyze(self, reference: Reference) -> Dict[str, Any]:
        """
        Analyze the reference and return score + explanation.
        
        Args:
            reference: Reference object to analyze
            
        Returns:
            Dictionary with:
                - score (int): Score from 0 to max_score
                - explanation (str): Human-readable explanation
                - details (dict, optional): Additional structured data
        """
        pass
    
    def _clamp_score(self, score: int) -> int:
        """
        Ensure score is within valid range [0, max_score].
        
        Args:
            score: Raw score value
            
        Returns:
            Clamped score
        """
        return max(0, min(score, self.max_score))