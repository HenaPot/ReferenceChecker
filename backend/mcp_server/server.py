# File: backend/mcp_server/server.py

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import refactored tools that delegate to strategies
from tools.check_reference_tool import check_reference
from tools.domain_tool import get_domain_reputation
from tools.metadata_tool import analyze_metadata
from tools.rag_tool import search_similar_sources


# Initialize MCP server
app = Server("reference-checker-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available tools for reference checking.
    
    All tools delegate to existing strategies - no duplicate logic!
    """
    return [
        Tool(
            name="check_reference",
            description=(
                "Perform comprehensive credibility analysis on a reference URL. "
                "Uses the CredibilityAnalyzer service which orchestrates all 4 strategies: "
                "Domain Reputation, Metadata Quality, Cross-Reference (RAG), and AI Analysis. "
                "This is the primary tool for complete reference checking."
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
                "Look up domain reputation using the DomainAnalysisStrategy. "
                "Returns credibility score (0-30), category (academic, government, news, etc.), "
                "and verification status. Useful for quick domain checks."
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
            name="analyze_metadata",
            description=(
                "Analyze metadata quality using the MetadataAnalysisStrategy. "
                "Evaluates completeness of author, publication date, and recency. "
                "Returns score (0-20) and detailed breakdown."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Article/paper title"
                    },
                    "author": {
                        "type": "string",
                        "description": "Author name(s)"
                    },
                    "publication_date": {
                        "type": "string",
                        "description": "Publication date (YYYY-MM-DD format)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="search_similar_sources",
            description=(
                "Search for similar credible sources using the RAGAnalysisStrategy. "
                "Uses vector similarity search across our database of verified sources. "
                "Returns score (0-25) based on number and quality of matches. "
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
    """
    Handle tool calls by delegating to refactored tools.
    
    All tools now use existing strategies - SINGLE SOURCE OF TRUTH!
    check_reference uses CredibilityAnalyzer which orchestrates all 4 strategies.
    """
    
    if name == "check_reference":
        # Full credibility analysis using CredibilityAnalyzer
        result = await check_reference(
            url=arguments.get("url"),
            title=arguments.get("title"),
            author=arguments.get("author"),
            publication_date=arguments.get("publication_date")
        )
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "get_domain_reputation":
        # Domain reputation using DomainAnalysisStrategy
        domain = arguments.get("domain")
        result = await get_domain_reputation(domain)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "analyze_metadata":
        # Metadata analysis using MetadataAnalysisStrategy
        result = await analyze_metadata(
            title=arguments.get("title"),
            author=arguments.get("author"),
            publication_date=arguments.get("publication_date")
        )
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "search_similar_sources":
        # RAG search using RAGAnalysisStrategy
        query = arguments.get("query")
        top_k = arguments.get("top_k", 5)
        result = await search_similar_sources(query, top_k)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


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