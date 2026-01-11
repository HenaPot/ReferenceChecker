# File: backend/app/services/n8n_service.py

import httpx
import asyncio
from typing import Dict, Any, Optional
from app.config import settings


class N8NService:
    """Service for integrating with N8N workflows."""
    
    def __init__(self):
        # Build full webhook URL from config
        if settings.N8N_WEBHOOK_BASE_URL:
            self.webhook_url = settings.N8N_WEBHOOK_BASE_URL + settings.N8N_REFERENCE_WEBHOOK
            self.enabled = True
        else:
            self.webhook_url = None
            self.enabled = False
    
    async def send_reference_analyzed(
        self,
        reference_id: str,
        url: str,
        title: Optional[str],
        author: Optional[str],
        domain: str,
        credibility_score: int,
        breakdown: Dict[str, Any]
    ) -> bool:
        """
        Send reference analysis to N8N webhook.
        
        Args:
            reference_id: UUID of the reference
            url: Reference URL
            title: Article title
            author: Article author
            domain: Domain name
            credibility_score: Total credibility score
            breakdown: Detailed score breakdown
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            print("⚠️  N8N webhook not configured (N8N_WEBHOOK_BASE_URL not set)")
            return False
        
        payload = {
            "event": "reference_analyzed",
            "reference_id": reference_id,
            "url": url,
            "title": title,
            "author": author,
            "domain": domain,
            "credibility_score": credibility_score,
            "breakdown": breakdown
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print(f"✅ N8N webhook success for reference {reference_id}")
                    return True
                else:
                    print(f"⚠️  N8N webhook returned {response.status_code}")
                    return False
                    
        except httpx.TimeoutException:
            print(f"⚠️  N8N webhook timeout")
            return False
        except Exception as e:
            print(f"❌ N8N webhook error: {e}")
            return False