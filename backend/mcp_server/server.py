# File: backend/mcp_server/server.py

import asyncio
import json
from datetime import datetime
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import our tools
from tools.domain_tool import get_domain_reputation
from tools.metadata_tool import analyze_metadata
from tools.rag_tool import search_similar_sources


# Initialize MCP server
app = Server("reference-checker-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for reference checking."""
    return [
        Tool(
            name="check_reference",
            description=(
                "Analyze a reference URL for credibility. Returns domain reputation, "
                "metadata quality assessment, and similar sources from our database. "
                "Use this to evaluate academic sources, news articles, and web content."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to check for credibility"
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional: Article/paper title"
                    },
                    "author": {
                        "type": "string",
                        "description": "Optional: Author name(s)"
                    },
                    "publication_date": {
                        "type": "string",
                        "description": "Optional: Publication date (YYYY-MM-DD format)"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="get_domain_reputation",
            description=(
                "Look up the reputation of a specific domain. Returns credibility score, "
                "category (academic, government, news, etc.), and verification status."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain to look up (e.g., 'nature.com', 'arxiv.org')"
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="search_similar_sources",
            description=(
                "Search for similar credible sources in our database based on topic/content. "
                "Useful for finding corroborating sources or related research."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'climate change machine learning', 'vaccine efficacy')"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    
    if name == "check_reference":
        # Full reference credibility check
        url = arguments.get("url")
        title = arguments.get("title")
        author = arguments.get("author")
        pub_date = arguments.get("publication_date")
        
        # Extract domain from URL
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace('www.', '').lower()
        
        # Get domain reputation
        domain_result = await get_domain_reputation(domain)
        
        # Analyze metadata
        metadata_result = await analyze_metadata(title, author, pub_date)
        
        # Search for similar sources
        search_query = title or f"content from {domain}"
        rag_result = await search_similar_sources(search_query, top_k=5)
        
        # Compile results
        total_score = (
            domain_result["score"] +
            metadata_result["score"] +
            rag_result["score"]
        )
        
        result = {
            "url": url,
            "domain": domain,
            "credibility_analysis": {
                "total_score": total_score,
                "max_score": 75,  # Domain (30) + Metadata (20) + RAG (25)
                "credibility_level": _get_credibility_level(total_score, 75),
                "breakdown": {
                    "domain": domain_result,
                    "metadata": metadata_result,
                    "similar_sources": rag_result
                }
            },
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "get_domain_reputation":
        domain = arguments.get("domain")
        result = await get_domain_reputation(domain)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "search_similar_sources":
        query = arguments.get("query")
        top_k = arguments.get("top_k", 5)
        result = await search_similar_sources(query, top_k)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


def _get_credibility_level(score: int, max_score: int) -> str:
    """Determine credibility level based on score percentage."""
    percentage = (score / max_score) * 100
    
    if percentage >= 80:
        return "highly_credible"
    elif percentage >= 60:
        return "credible"
    elif percentage >= 40:
        return "questionable"
    elif percentage >= 20:
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