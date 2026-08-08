"""
app/rag/embeddings.py

Provides a lazily-loaded embedding model for the RAG pipeline.
The model is loaded once per process and reused for subsequent
document and query embedding operations.
"""

from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings

from app.rag.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Return the local embedding model.

    The model is downloaded on the first call and cached in memory.
    Subsequent calls reuse the same model.
    """
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)


def embed_query(text: str) -> list[float]:
    """Generate an embedding vector for a single query."""
    return get_embedding_model().embed_query(text)


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Generate embedding vectors for multiple document chunks."""
    return get_embedding_model().embed_documents(texts)
