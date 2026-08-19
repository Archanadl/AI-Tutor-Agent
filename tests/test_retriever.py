import pytest

from app.rag.retriever import retrieve


DOCUMENT_ID = "research_report.pdf"


def test_retrieve_returns_documents_for_relevant_question():
    documents = retrieve(
        question="What is quantum computing?",
        document_id=DOCUMENT_ID,
        k=3,
    )

    assert isinstance(documents, list)
    assert len(documents) > 0

    for document in documents:
        assert document.page_content
        assert document.metadata.get("document_id") == DOCUMENT_ID
        assert "relevance_score" in document.metadata


def test_retrieve_rejects_empty_question():
    with pytest.raises(ValueError, match="Question cannot be empty"):
        retrieve(
            question="",
            document_id=DOCUMENT_ID,
        )


def test_retrieve_rejects_missing_document_id():
    with pytest.raises(ValueError, match="document_id cannot be empty"):
        retrieve(
            question="What is quantum computing?",
            document_id="",
        )