"""
mcp_server/web_search_node.py

LangGraph-compatible node that calls the local MCP server's ``web_search``
tool and appends the results to the CRAG pipeline's ``context`` list.

This replaces the static ``fallback_node`` in ``app/graph.py``.  Instead of
returning a canned apology, it performs a live DuckDuckGo web search via
the FastMCP server and feeds the results into the ``generate`` node.

State mutations:
    * Extends ``state["context"]`` with ``Document`` objects whose
      ``metadata["source"]`` is the result URL.

Usage in the LangGraph ``StateGraph``::

    from mcp_server.web_search_node import web_search_node

    workflow.add_node("web_search", web_search_node)
"""

from __future__ import annotations

import asyncio
import json
import logging

from langchain_core.documents import Document

logger = logging.getLogger("mcp_server.web_search_node")

# ---------------------------------------------------------------------------
# MCP server connection defaults
# ---------------------------------------------------------------------------
MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"
DEFAULT_MAX_RESULTS = 3


# ---------------------------------------------------------------------------
# Async implementation — talks to the local FastMCP server
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

async def _async_web_search_node(state: dict) -> dict:
    """Async LangGraph node that performs a web search via the MCP server.

    Reads ``student_question`` and ``context`` from ``TutorState``.
    """
    question = state.get("student_question", "")
    existing_context = state.get("context", [])

    logger.info("MCP web_search_node invoked for question=%r", question)

    search_results = await _call_mcp_web_search(question)

    if not search_results:
        logger.info("No web results returned; keeping existing context")
        return {
            "context": existing_context,
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
        "MCP web_search_node appending %d web documents", len(web_documents)
    )

    return {
        "context": existing_context + web_documents,
    }


# ---------------------------------------------------------------------------
# Sync wrapper (drop-in compatible with the existing sync graph)
# ---------------------------------------------------------------------------

def web_search_node(state: dict) -> dict:
    """Synchronous LangGraph node — drop-in replacement for the
    ``fallback_node`` in ``app/graph.py``.

    Internally runs the async MCP client via ``asyncio.run()``.  If an
    event loop is already running (e.g. inside Jupyter or Streamlit),
    it falls back to running in a separate thread.
    """
    try:
        # Fast path: no loop running → use asyncio.run()
        return asyncio.run(_async_web_search_node(state))
    except RuntimeError:
        # An event loop is already running (Jupyter, Streamlit, etc.)
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, _async_web_search_node(state))
            return future.result(timeout=30)
