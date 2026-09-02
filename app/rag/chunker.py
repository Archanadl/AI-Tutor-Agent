from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.config import settings


def chunk_pages(
    pages: list[Document],
    document_id: str,
    source_name: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Document]:
    """
    Split PDF pages into chunks and attach metadata required
    by the downstream RAG pipeline.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=(
            chunk_size
            if chunk_size is not None
            else settings.chunk_size
        ),
        chunk_overlap=(
            chunk_overlap
            if chunk_overlap is not None
            else settings.chunk_overlap
        ),
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(pages)

    for i, chunk in enumerate(chunks):
        chunk.metadata.update(
            {
                "document_id": document_id,
                "source": source_name,
                "chunk_index": i,
            }
        )

    return chunks