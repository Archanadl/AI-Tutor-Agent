from app.rag.retriever import retrieve


DOCUMENT_ID = "research_report.pdf"


def test_rag_retrieves_quantum_computing_content():
    documents = retrieve(
        question="What is quantum computing?",
        document_id=DOCUMENT_ID,
    )

    assert len(documents) > 0

    combined_text = " ".join(
        document.page_content.lower()
        for document in documents
    )

    assert "quantum" in combined_text


def test_rag_retrieves_quantum_challenges_content():
    documents = retrieve(
        question="What are the challenges of quantum computing?",
        document_id=DOCUMENT_ID,
    )

    assert len(documents) > 0

    combined_text = " ".join(
        document.page_content.lower()
        for document in documents
    )

    assert "quantum" in combined_text


def test_rag_returns_ranked_documents():
    documents = retrieve(
        question="What is quantum computing?",
        document_id=DOCUMENT_ID,
    )

    assert len(documents) > 0

    scores = [
        document.metadata.get("relevance_score")
        for document in documents
    ]

    assert all(score is not None for score in scores)