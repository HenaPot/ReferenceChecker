# File: backend/mcp_server_standalone.py
# This is a standalone script that can be run directly without module imports

import asyncio
import json
import os
import sys
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer

# Import models and config
from app.models import DomainReputation, RAGSource
from app.config import settings


# Initialize database
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


# Initialize MCP server
app = Server("reference-checker-mcp")


# ========== TOOL FUNCTIONS ==========

async def get_domain_reputation_tool(domain: str) -> Dict[str, Any]:
    """Look up domain reputation in the database."""
    db = SessionLocal()
    
    try:
        domain_rep = db.query(DomainReputation).filter(
            DomainReputation.domain_name == domain
        ).first()
        
        if domain_rep:
            return {
                "domain": domain,
                "score": domain_rep.base_score,
                "max_score": 30,
                "category": domain_rep.category.value,
                "verified": domain_rep.is_verified,
                "explanation": f"Domain {domain} is a {'verified' if domain_rep.is_verified else 'catalogued'} {domain_rep.category.value} source. Score: {domain_rep.base_score}/30"
            }
        else:
            # Unknown domain heuristics
            domain_lower = domain.lower()
            
            if domain_lower.endswith('.edu'):
                score, category = 25, "academic"
            elif domain_lower.endswith('.gov'):
                score, category = 25, "government"
            elif any(kw in domain_lower for kw in ['university', 'academic', 'research', 'scholar', 'institute']):
                score, category = 15, "academic"
            else:
                score, category = 10, "unknown"
            
            return {
                "domain": domain,
                "score": score,
                "max_score": 30,
                "category": category,
                "verified": False,
                "explanation": f"Domain {domain} is not in our database. Score: {score}/30 based on heuristics."
            }
    finally:
        db.close()


async def analyze_metadata_tool(
    title: Optional[str] = None,
    author: Optional[str] = None,
    publication_date: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze metadata quality."""
    score = 0
    details = []
    
    # Author (10 points)
    if author and author.strip():
        score += 10
        details.append(f"✓ Author: {author}")
    else:
        details.append("✗ No author (-10 pts)")
    
    # Publication date (5 points)
    if publication_date:
        try:
            pub_date = datetime.fromisoformat(publication_date).date()
            score += 5
            details.append(f"✓ Date: {pub_date}")
            
            # Recency (5 points)
            age_days = (date.today() - pub_date).days
            years_old = age_days / 365.25
            
            if years_old <= 2:
                score += 5
                details.append(f"✓ Recent ({years_old:.1f}y, +5 pts)")
            elif years_old <= 5:
                score += 3
                details.append(f"○ Moderately recent (+3 pts)")
            elif years_old <= 10:
                score += 1
                details.append(f"○ Older (+1 pt)")
        except:
            details.append("⚠ Invalid date format")
    else:
        details.append("✗ No date (-10 pts)")
    
    return {
        "score": score,
        "max_score": 20,
        "explanation": f"Metadata: {score}/20. " + " ".join(details)
    }


async def search_similar_sources_tool(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Search for similar sources in RAG database."""
    db = SessionLocal()
    
    try:
        model = get_embedding_model()
        query_embedding = model.encode(query).tolist()
        
        all_sources = db.query(RAGSource).filter(
            RAGSource.embedding_vector.isnot(None)
        ).all()
        
        if not all_sources:
            return {
                "score": 5,
                "max_score": 25,
                "similar_sources": [],
                "count": 0,
                "explanation": "No sources in RAG database."
            }
        
        similarities = []
        for source in all_sources:
            try:
                stored_embedding = json.loads(source.embedding_vector)
                similarity = cosine_similarity(query_embedding, stored_embedding)
                
                similarities.append({
                    "url": source.url,
                    "title": source.title,
                    "domain": source.domain,
                    "similarity": round(similarity, 3)
                })
            except:
                continue
        
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        top_sources = [s for s in similarities[:top_k] if s["similarity"] >= 0.3]
        
        if not top_sources:
            score = 5
            explanation = "No similar sources found."
        else:
            avg_sim = sum(s["similarity"] for s in top_sources) / len(top_sources)
            
            if len(top_sources) >= 5 and avg_sim >= 0.6:
                score = 25
            elif len(top_sources) >= 3:
                score = 20
            elif len(top_sources) >= 2:
                score = 15
            else:
                score = 10
            
            explanation = f"Found {len(top_sources)} similar sources (avg similarity: {avg_sim:.2f})"
        
        return {
            "score": score,
            "max_score": 25,
            "similar_sources": top_sources,
            "count": len(top_sources),
            "explanation": explanation
        }
    finally:
        db.close()


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity."""
    if len(vec1) != len(vec2):
        return 0.0
    
    dot = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = sum(a * a for a in vec1) ** 0.5
    mag2 = sum(b * b for b in vec2) ** 0.5
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    return max(0.0, min(1.0, dot / (mag1 * mag2)))


# ========== MCP SERVER HANDLERS ==========

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="check_reference",
            description="Analyze a reference URL for credibility (domain + metadata + similar sources)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to check"},
                    "title": {"type": "string", "description": "Optional title"},
                    "author": {"type": "string", "description": "Optional author"},
                    "publication_date": {"type": "string", "description": "Optional date (YYYY-MM-DD)"}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="get_domain_reputation",
            description="Look up domain reputation and credibility score",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Domain to look up"}
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="search_similar_sources",
            description="Find similar credible sources on a topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "top_k": {"type": "integer", "description": "Number of results", "default": 5}
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    
    try:
        if name == "check_reference":
            url = arguments.get("url")
            title = arguments.get("title")
            author = arguments.get("author")
            pub_date = arguments.get("publication_date")
            
            # Extract domain
            domain = urlparse(url).netloc.replace('www.', '').lower()
            
            # Run all analyses
            domain_result = await get_domain_reputation_tool(domain)
            metadata_result = await analyze_metadata_tool(title, author, pub_date)
            rag_result = await search_similar_sources_tool(title or f"content from {domain}", top_k=5)
            
            total_score = domain_result["score"] + metadata_result["score"] + rag_result["score"]
            
            result = {
                "url": url,
                "domain": domain,
                "total_score": total_score,
                "max_score": 75,
                "credibility_level": get_credibility_level(total_score, 75),
                "breakdown": {
                    "domain": domain_result,
                    "metadata": metadata_result,
                    "similar_sources": rag_result
                }
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_domain_reputation":
            domain = arguments.get("domain")
            result = await get_domain_reputation_tool(domain)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "search_similar_sources":
            query = arguments.get("query")
            top_k = arguments.get("top_k", 5)
            result = await search_similar_sources_tool(query, top_k)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        error_result = {"error": str(e), "tool": name}
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


def get_credibility_level(score: int, max_score: int) -> str:
    """Determine credibility level."""
    pct = (score / max_score) * 100
    
    if pct >= 80:
        return "highly_credible"
    elif pct >= 60:
        return "credible"
    elif pct >= 40:
        return "questionable"
    elif pct >= 20:
        return "unreliable"
    else:
        return "highly_unreliable"


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())