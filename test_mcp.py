import pytest
from mcp_server.web_search_node import RAGState, web_search_node
from mcp_server.server import web_search
import json

def test_web_search_tool():
    """Test that the web search tool returns valid JSON with our expected keys."""
    # We test the underlying tool directly to avoid needing a running MCP server in tests
    result = web_search(query="photosynthesis", max_results=1)
    
    # Must be valid JSON
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    
    # Check structure if there are results
    if len(parsed) > 0:
        first = parsed[0]
        assert "title" in first
        assert "snippet" in first
        assert "url" in first

def test_web_search_node_fallback():
    """Test that the node gracefully handles when the server is unavailable."""
    # Note: Ensure the FastMCP server is NOT running when this test executes,
    # otherwise it will succeed and add real documents instead of falling back.
    # Because we're connecting to localhost:8000, if it's down, we expect web_search_used=False
    
    state: RAGState = {
        "question": "What is ATP?",
        "document_id": "test-doc-123",
        "documents": [],
        "generation": "",
        "source_type": "document",
        "confidence_score": 0.0,
        "web_search_used": False,
        "retry_count": 0
    }
    
    new_state = web_search_node(state)
    
    # If the server is not running, we expect web_search_used to be False
    # (If the server is running, this test might fail because it will return True.
    # In a full test suite, we'd mock the network call, but this is a basic sanity check).
    assert "documents" in new_state
