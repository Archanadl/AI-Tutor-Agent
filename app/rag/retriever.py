"""
app/rag/retriever.py

Retrieves the most relevant chunks from ChromaDB
for a user's question.
"""
from langchain_core.documents import Document

# These imports assume your teammates have created these files!
from app.rag.vector_store import similarity_search
from app.rag.config import settings

def retrieve(
    question: str,
    document_id: str,
    k: int | None = None,
) -> list[Document]:
    """
    Retrieve the most relevant document chunks for a question.
    """
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not document_id:
        raise ValueError("document_id cannot be empty.")

    results = similarity_search(
        query=question,
        document_id=document_id,
        k=k if k is not None else settings.retrieval_k,
    )

    documents = []

    for document, distance in results:
        relevance_score = 1 / (1 + distance)

        if distance <= settings.max_retrieval_distance:
            document.metadata["relevance_score"] = relevance_score
            documents.append(document)

    return documents