# File: backend/app/services/credibility_analyzer.py

from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
import uuid

from app.models import Reference, CredibilityReport
from app.models.reference import ReferenceStatus
from app.strategies.domain_strategy import DomainAnalysisStrategy
from app.strategies.metadata_strategy import MetadataAnalysisStrategy
from app.strategies.rag_strategy import RAGAnalysisStrategy
from app.strategies.ai_strategy import AIAnalysisStrategy


class CredibilityAnalyzer:
    """
    Main orchestrator for credibility analysis.
    
    Coordinates multiple analysis strategies to produce a comprehensive
    credibility score and report for academic/research references.
    """
    
    def __init__(self, db: Session):
        """
        Initialize analyzer with database session and strategies.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        
        # Initialize all analysis strategies
        self.strategies = [
            DomainAnalysisStrategy(db),      # 30 points max
            MetadataAnalysisStrategy(db),    # 20 points max
            RAGAnalysisStrategy(db),         # 25 points max
            AIAnalysisStrategy(db)           # 25 points max
        ]
        
        # Total possible score: 100 points
        self.max_score = sum(strategy.max_score for strategy in self.strategies)
    
    async def analyze_reference(self, reference: Reference) -> CredibilityReport:
        """
        Analyze a reference and create a credibility report.
        
        This is the main entry point for credibility analysis.
        
        Args:
            reference: Reference object to analyze
            
        Returns:
            CredibilityReport object with complete analysis
        """
        # CRITICAL FIX: Delete any existing report first (for reanalysis)
        existing_report = self.db.query(CredibilityReport).filter(
            CredibilityReport.reference_id == reference.reference_id
        ).first()
        
        if existing_report:
            self.db.delete(existing_report)
            self.db.commit()
        
        # Execute all strategies and store results
        domain_result = {"score": 0, "explanation": "Not analyzed"}
        metadata_result = {"score": 0, "explanation": "Not analyzed"}
        rag_result = {"score": 0, "explanation": "Not analyzed"}
        ai_result = {"score": 0, "explanation": "Not analyzed"}
        red_flags = []
        
        # Run Domain Strategy
        try:
            domain_result = self.strategies[0].analyze(reference)
            if domain_result["score"] < 10:
                red_flags.append("Low domain reputation")
        except Exception as e:
            domain_result = {"score": 0, "explanation": f"Domain analysis failed: {str(e)}"}
            red_flags.append("Domain analysis error")
        
        # Run Metadata Strategy
        try:
            metadata_result = self.strategies[1].analyze(reference)
            if metadata_result["score"] < 5:
                red_flags.append("Poor metadata quality")
        except Exception as e:
            metadata_result = {"score": 0, "explanation": f"Metadata analysis failed: {str(e)}"}
            red_flags.append("Metadata analysis error")
        
        # Run RAG Strategy
        try:
            rag_result = self.strategies[2].analyze(reference)
            if rag_result.get("details", {}).get("count", 0) == 0:
                red_flags.append("No corroborating sources found")
        except Exception as e:
            rag_result = {"score": 0, "explanation": f"RAG analysis failed: {str(e)}"}
            red_flags.append("RAG analysis error")
        
        # Run AI Strategy
        try:
            ai_result = self.strategies[3].analyze(reference)
            if ai_result["score"] < 10:
                red_flags.append("AI flagged content quality concerns")
        except Exception as e:
            ai_result = {"score": 0, "explanation": f"AI analysis failed: {str(e)}"}
            red_flags.append("AI analysis error")
        
        # Calculate total score
        total_score = (
            domain_result["score"] +
            metadata_result["score"] +
            rag_result["score"] +
            ai_result["score"]
        )
        
        # Create credibility report matching YOUR exact model structure
        report = CredibilityReport(
            report_id=uuid.uuid4(),
            reference_id=reference.reference_id,
            
            # Individual scores (matching your model exactly)
            domain_score=domain_result["score"],
            metadata_score=metadata_result["score"],
            rag_score=rag_result["score"],
            ai_score=ai_result["score"],
            total_score=total_score,
            
            # Explanations (matching your model exactly)
            domain_explanation=domain_result["explanation"],
            metadata_explanation=metadata_result["explanation"],
            rag_explanation=rag_result["explanation"],
            ai_explanation=ai_result["explanation"],
            
            # Red flags
            red_flags=red_flags,
            
            # Timestamp
            created_at=datetime.utcnow()
        )
        
        # Save to database
        self.db.add(report)
        
        # Update reference status and score
        reference.status = ReferenceStatus.completed
        reference.credibility_score = total_score
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def get_report_by_reference(self, reference_id: uuid.UUID) -> CredibilityReport:
        """
        Get existing credibility report for a reference.
        
        Args:
            reference_id: UUID of the reference
            
        Returns:
            CredibilityReport object or None
        """
        return self.db.query(CredibilityReport).filter(
            CredibilityReport.reference_id == reference_id
        ).first()
    
    async def reanalyze_reference(self, reference: Reference) -> CredibilityReport:
        """
        Re-run analysis on an existing reference.
        
        The old report is automatically deleted in analyze_reference().
        
        Args:
            reference: Reference object to reanalyze
            
        Returns:
            New CredibilityReport object
        """
        # Mark reference as processing
        reference.status = ReferenceStatus.processing
        reference.credibility_score = None
        self.db.commit()
        
        # Run new analysis (which will delete old report automatically)
        return await self.analyze_reference(reference)