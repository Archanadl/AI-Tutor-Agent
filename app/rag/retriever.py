"""
app/rag/retriever.py

Retrieves the most relevant chunks from ChromaDB
for a user's question.
"""

from langchain_core.documents import Document

from app.rag.vector_store import similarity_search
from app.rag.config import settings


def retrieve(
    question: str,
    document_id: str,
    k: int | None = None,
) -> list[Document]:
    """
    Retrieve the most relevant document chunks for a question.

    Args:
        question: User's question.
        document_id: ID of the PDF/document.
        k: Number of chunks to retrieve.

    Returns:
        List of relevant Document objects.
    """

    results = similarity_search(
        query=question,
        document_id=document_id,
        k=k or settings.retrieval_k,
    )

    documents = []

    for document, score in results:
        if score >= settings.min_relevance_score:
            documents.append(document)

    return documents