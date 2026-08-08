"""
mcp_server/web_search_node.py

LangGraph-compatible node that calls the local MCP server's ``web_search``
tool and appends the results to the CRAG pipeline's ``documents`` list.

This is a **drop-in replacement** for the Tavily-based ``web_search_node``
in ``app/rag/retriever.py``.  It produces the exact same state mutations:

* Extends ``state["documents"]`` with ``Document`` objects whose
  ``metadata["source"]`` is the result URL.
* Sets ``state["web_search_used"]`` to ``True`` on success.

Usage in the LangGraph ``StateGraph``::

    from mcp_server.web_search_node import web_search_node

    workflow.add_node("web_search", web_search_node)
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING

from langchain_core.documents import Document

if TYPE_CHECKING:
    # Avoid circular / heavy imports at module level; the type is only
    # used for annotation.  At runtime RAGState is just a TypedDict so
    # any conforming dict works.
    from app.rag.retriever import RAGState

logger = logging.getLogger("mcp_server.web_search_node")

# ---------------------------------------------------------------------------
# MCP server connection defaults
# ---------------------------------------------------------------------------
MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"
DEFAULT_MAX_RESULTS = 3


# ---------------------------------------------------------------------------
# Async implementation
# ---------------------------------------------------------------------------

async def _call_mcp_web_search(
    query: str,
    max_results: int = DEFAULT_MAX_RESULTS,
    server_url: str = MCP_SERVER_URL,
) -> list[dict]:
    """Connect to the local MCP server and invoke the ``web_search`` tool.

    Returns a list of dicts with ``title``, ``snippet``, ``url`` keys,
    or an empty list if the server is unreachable / returns an error.
    """
    try:
        from fastmcp import Client
        from fastmcp.client.transports import StreamableHttpTransport
    except ImportError:
        logger.error(
            "fastmcp is not installed. "
            "Install it with: pip install fastmcp==3.4.6"
        )
        return []

    transport = StreamableHttpTransport(url=server_url)
    client = Client(transport)

    try:
        async with client:
            result = await client.call_tool(
                "web_search",
                {
                    "query": query,
                    "max_results": max_results,
                },
            )

            # fastmcp 3.4.6 returns a CallToolResult with a .data
            # attribute that contains the tool's return value directly.
            raw = None

            if hasattr(result, "data") and result.data:
                raw = result.data
            elif hasattr(result, "content"):
                # Fallback: iterate over content blocks for text
                for block in (result.content or []):
                    text = getattr(block, "text", None)
                    if text:
                        raw = text
                        break

            if raw is None:
                logger.warning("Empty MCP result for query=%r", query)
                return []

            if isinstance(raw, str):
                return json.loads(raw)
            if isinstance(raw, list):
                return raw

            logger.warning("Unexpected MCP data type: %s", type(raw))
            return []

    except ConnectionError:
        logger.warning(
            "Could not connect to MCP server at %s. "
            "Is it running?  Start it with: python -m mcp_server.server",
            server_url,
        )
        return []
    except Exception:
        logger.exception("MCP web_search call failed")
        return []


# ---------------------------------------------------------------------------
# Async node (for async LangGraph graphs)
# ---------------------------------------------------------------------------

async def async_web_search_node(state: "RAGState") -> "RAGState":
    """Async LangGraph node — use if the graph is compiled with
    ``workflow.compile()`` in an async context.
    """
    question = state["question"]
    logger.info("MCP web_search_node invoked for question=%r", question)

    search_results = await _call_mcp_web_search(question)

    if not search_results:
        logger.info("No web results returned; marking web_search_used=False")
        return {
            **state,
            "web_search_used": False,
        }

    web_documents: list[Document] = []
    for item in search_results:
        snippet = item.get("snippet", "")
        if snippet:
            web_documents.append(
                Document(
                    page_content=snippet,
                    metadata={
                        "source": item.get("url", "web"),
                        "title": item.get("title", ""),
                    },
                )
            )

    logger.info(
        "MCP web_search_node appending %d documents", len(web_documents)
    )

    return {
        **state,
        "documents": state["documents"] + web_documents,
        "web_search_used": True,
    }


# ---------------------------------------------------------------------------
# Sync wrapper (drop-in compatible with the existing sync graph)
# ---------------------------------------------------------------------------

def web_search_node(state: "RAGState") -> "RAGState":
    """Synchronous LangGraph node — drop-in replacement for the existing
    Tavily-based ``web_search_node`` in ``app/rag/retriever.py``.

    Internally runs the async MCP client via ``asyncio.run()``.  If an
    event loop is already running (e.g. inside Jupyter), it falls back
    to ``nest_asyncio`` or creates a new thread.
    """
    try:
        # Fast path: no loop running → use asyncio.run()
        return asyncio.run(async_web_search_node(state))
    except RuntimeError:
        # An event loop is already running (Jupyter, Streamlit, etc.)
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, async_web_search_node(state))
            return future.result(timeout=30)
