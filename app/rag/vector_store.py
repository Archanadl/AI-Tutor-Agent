"""
app/rag/vector_store.py

Owns all direct interaction with ChromaDB: adding chunks, deleting a
document's chunks, and low-level similarity search. retriever.py builds on
top of this — this module has no knowledge of grading, generation, or the
RAG pipeline, it's purely storage.
"""

from functools import lru_cache
from langchain_core.documents import Document
from langchain_chroma import Chroma

from app.rag.config import settings
from app.rag.embeddings import get_embedding_model


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    """
    Single shared Chroma collection for all documents. Documents are
    isolated from each other via the 'document_id' metadata field rather
    than separate collections — this keeps retrieval fast and avoids
    collection-management overhead as the number of uploaded PDFs grows.
    """
    return Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embedding_model(),
        persist_directory=settings.chroma_persist_dir,
    )


def add_chunks(chunks: list[Document]) -> None:
    """Embeds and stores a list of already-chunked, already-tagged Documents."""
    if not chunks:
        return
    get_vectorstore().add_documents(chunks)


def delete_document(document_id: str) -> None:
    """Removes all chunks belonging to a document (e.g. if the user deletes an upload)."""
    vectorstore = get_vectorstore()
    vectorstore._collection.delete(where={"document_id": document_id})


def similarity_search(
    query: str,
    document_id: str = None,
    k: int = None,
) -> list[tuple[Document, float]]:
    """
    Low-level similarity search, optionally scoped to a single document.
    Returns (Document, relevance_score) tuples, score normalized 0-1
    (higher = more relevant).
    """
    vectorstore = get_vectorstore()
    filter_dict = {"document_id": document_id} if document_id else None

    return vectorstore.similarity_search_with_relevance_scores(
        query,
        k=k or settings.retrieval_k,
        filter=filter_dict,
    )


def get_all_chunks_for_document(document_id: str) -> list[str]:
    """Fetches every stored chunk's raw text for a document — used by summarization."""
    vectorstore = get_vectorstore()
    result = vectorstore.get(where={"document_id": document_id})
    return result.get("documents", [])