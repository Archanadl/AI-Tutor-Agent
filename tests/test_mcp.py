"""
Tests for the MCP server tool and the LangGraph web_search_node.
"""

import json
import pytest

from mcp_server.server import web_search
from mcp_server.web_search_node import web_search_node


def test_web_search_tool():
    """Test that the web search tool returns valid JSON with expected keys."""
    result = web_search(query="photosynthesis", max_results=1)

    parsed = json.loads(result)
    assert isinstance(parsed, list)

    if len(parsed) > 0:
        first = parsed[0]
        assert "title" in first
        assert "snippet" in first
        assert "url" in first


def test_web_search_node_without_server():
    """Test that the node gracefully handles when the MCP server is down.

    When the FastMCP server is NOT running, the node should return
    the existing context unchanged (no crash).
    """
    state = {
        "student_question": "What is ATP?",
        "document_id": "test-doc-123",
        "context": [],
        "relevant": False,
        "student_answer": "",
    }

    new_state = web_search_node(state)

    # Must always return a dict with "context"
    assert "context" in new_state
    assert isinstance(new_state["context"], list)
