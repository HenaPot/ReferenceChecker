# File: backend/app/strategies/ai_strategy.py

from typing import Dict, Any
import json
from sqlalchemy.orm import Session
from anthropic import Anthropic

from app.models import Reference
from app.strategies.base_strategy import AnalysisStrategy
from app.config import settings


class AIAnalysisStrategy(AnalysisStrategy):
    """
    Analyzes reference credibility using Claude AI for content quality assessment.
    
    Evaluates:
    - Writing quality and professionalism
    - Presence of citations and references
    - Bias indicators and emotional language
    - Factual specificity vs vague claims
    
    Maximum: 25 points
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    @property
    def name(self) -> str:
        return "AI Content Analysis (Claude)"
    
    @property
    def max_score(self) -> int:
        return 25
    
    def analyze(self, reference: Reference) -> Dict[str, Any]:
        """
        Use Claude AI to analyze reference content quality.
        
        Args:
            reference: Reference object to analyze
            
        Returns:
            Dictionary with score, explanation, and AI analysis details
        """
        # For now, we only have basic metadata (title, author, domain, URL)
        # Full content analysis would require web scraping
        # Let's do a simple analysis based on available metadata
        
        if not reference.title and not reference.author:
            return {
                "score": 5,
                "explanation": "Insufficient information for AI analysis. "
                              "Default score of 5/25 assigned.",
                "details": {
                    "ai_analysis": "No content available for analysis"
                }
            }
        
        try:
            # Prepare prompt for Claude
            prompt = self._create_analysis_prompt(reference)
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            ai_response = response.content[0].text
            
            # Extract score and analysis from AI response
            score, analysis = self._parse_ai_response(ai_response)
            
            return {
                "score": self._clamp_score(score),
                "explanation": analysis,
                "details": {
                    "ai_analysis": ai_response,
                    "model": "claude-sonnet-4-20250514"
                }
            }
        
        except Exception as e:
            # If AI analysis fails, return conservative score
            return {
                "score": 10,
                "explanation": f"AI analysis encountered an error. "
                              f"Conservative score of 10/25 assigned. Error: {str(e)}",
                "details": {
                    "ai_analysis": f"Error: {str(e)}",
                    "error": True
                }
            }
    
    def _create_analysis_prompt(self, reference: Reference) -> str:
        """
        Create prompt for Claude to analyze the reference.
        
        Args:
            reference: Reference object
            
        Returns:
            Analysis prompt
        """
        metadata = {
            "url": reference.url,
            "domain": reference.domain,
            "title": reference.title,
            "author": reference.author,
            "publication_date": str(reference.publication_date) if reference.publication_date else None
        }
        
        return f"""You are analyzing an academic/research reference for credibility. 
Based on the metadata provided, assess the following criteria and provide a credibility score from 0-25:

Reference Metadata:
{json.dumps(metadata, indent=2)}

Evaluation Criteria:
1. Title Quality (0-8 points):
   - Is the title descriptive and specific?
   - Does it use professional academic language?
   - Are there any red flags (clickbait, excessive claims)?

2. Source Professionalism (0-8 points):
   - Does the domain suggest a credible publisher?
   - Is author information provided?
   - Does the publication date indicate recency?

3. Content Indicators (0-9 points):
   - Based on title/metadata, does this appear to be:
     * Peer-reviewed research
     * Evidence-based reporting
     * Opinion/blog content
     * Marketing/promotional material

Provide your response in this exact format:
SCORE: [number from 0-25]
ANALYSIS: [2-3 sentence explanation of your assessment]

Be critical but fair. Academic sources should score higher, but good journalism can also score well."""
    
    def _parse_ai_response(self, ai_response: str) -> tuple[int, str]:
        """
        Parse Claude's response to extract score and analysis.
        
        Args:
            ai_response: Raw response from Claude
            
        Returns:
            Tuple of (score, analysis)
        """
        lines = ai_response.strip().split('\n')
        score = 10  # Default
        analysis = "AI analysis completed."
        
        for line in lines:
            if line.startswith("SCORE:"):
                try:
                    score = int(line.split("SCORE:")[1].strip())
                except (ValueError, IndexError):
                    pass
            elif line.startswith("ANALYSIS:"):
                analysis = line.split("ANALYSIS:")[1].strip()
        
        # If we didn't find structured format, use whole response as analysis
        if "SCORE:" not in ai_response:
            analysis = ai_response
            # Try to infer score from keywords
            if any(word in ai_response.lower() for word in ["excellent", "high quality", "credible"]):
                score = 20
            elif any(word in ai_response.lower() for word in ["good", "reliable"]):
                score = 15
            elif any(word in ai_response.lower() for word in ["poor", "unreliable", "questionable"]):
                score = 5
        
        return score, analysis