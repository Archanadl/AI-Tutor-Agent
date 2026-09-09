"""
mcp_server/server.py

FastMCP server exposing a zero-cost DuckDuckGo web-search tool for the
AI-Tutor CRAG pipeline.

Run locally:
    python -m mcp_server.server

The server listens on http://127.0.0.1:8001/mcp.
FastAPI continues to use port 8000.
"""

from __future__ import annotations

import json
import logging

from fastmcp import FastMCP


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("mcp_server")


# ---------------------------------------------------------------------------
# FastMCP instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "AI-Tutor-Search",
    instructions=(
        "Educational web-search server for the AI-Tutor CRAG pipeline. "
        "Provides a DuckDuckGo-powered search tool that returns concise, "
        "educational results with no API key required."
    ),
)


# ---------------------------------------------------------------------------
# Tool: web_search
# ---------------------------------------------------------------------------

@mcp.tool()
def web_search(query: str, max_results: int = 3) -> str:
    """Search the web for educational content using DuckDuckGo.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return.

    Returns:
        JSON string containing search results.
    """

    DDGS = None

    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            pass

    if DDGS is None:
        logger.error(
            "Neither 'ddgs' nor 'duckduckgo_search' is installed. "
            "Install with: pip install ddgs"
        )
        return json.dumps([])

    logger.info(
        "web_search called — query=%r, max_results=%d",
        query,
        max_results,
    )

    try:
        with DDGS() as ddgs:
            raw_results = ddgs.text(
                query,
                max_results=max_results,
            )

        results = [
            {
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", ""),
            }
            for r in raw_results
        ]

        logger.info(
            "web_search returned %d results",
            len(results),
        )

        return json.dumps(results)

    except TimeoutError:
        logger.warning(
            "web_search timed out for query=%r",
            query,
        )
        return json.dumps([])

    except Exception:
        logger.exception(
            "web_search failed for query=%r",
            query,
        )
        return json.dumps([])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info(
        "Starting AI-Tutor-Search MCP server "
        "on http://127.0.0.1:8001/mcp"
    )

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
        path="/mcp",
    )