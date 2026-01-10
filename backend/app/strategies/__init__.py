# File: backend/app/strategies/__init__.py

"""
Credibility analysis strategies package.

This package implements the Strategy Pattern for modular credibility analysis.
Each strategy analyzes a different aspect of reference credibility.
"""

from app.strategies.base_strategy import AnalysisStrategy
from app.strategies.domain_strategy import DomainAnalysisStrategy
from app.strategies.metadata_strategy import MetadataAnalysisStrategy
from app.strategies.rag_strategy import RAGAnalysisStrategy
from app.strategies.ai_strategy import AIAnalysisStrategy

__all__ = [
    "AnalysisStrategy",
    "DomainAnalysisStrategy",
    "MetadataAnalysisStrategy",
    "RAGAnalysisStrategy",
    "AIAnalysisStrategy",
]