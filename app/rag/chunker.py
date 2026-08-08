"""
app/rag/chunker.py

Splits parsed PDF pages into overlapping chunks sized for embedding, and
attaches the metadata every downstream feature depends on:
  - document_id  -> per-document retrieval scoping
  - source       -> source-grounding badges in the chat UI
  - chunk_index  -> ordering, used by concept-dependency-graph logic
  - page         -> already set by pdf_parser.py, preserved through the split
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.config import settings


def chunk_pages(
    pages: list[Document],
    document_id: str,
    source_name: str,
    chunk_size: int | None = None,
    chunk_overlap: int = None,
) -> list[Document]:
    """
    Splits pages into chunks and tags each chunk with the metadata needed
    by vector_store.py, retriever.py, and other features downstream.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.chunk_size,
        chunk_overlap=chunk_overlap or settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(pages)

    for i, chunk in enumerate(chunks):
        chunk.metadata.update({
            "document_id": document_id,
            "source": source_name,
            "chunk_index": i,
            # "page" is inherited automatically from the parent Document's metadata
        })

    return chunks