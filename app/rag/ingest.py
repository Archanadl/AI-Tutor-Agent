from pathlib import Path

from app.rag.pdf_parser import parse_pdf
from app.rag.chunker import chunk_pages
from app.rag.vector_store import add_chunks


def ingest_pdf(
    file_path: str,
    document_id: str | None = None,
) -> dict:
    """
    Parse a PDF, split it into chunks, and store the chunks in ChromaDB.

    Args:
        file_path: Path to the PDF file.
        document_id: Optional ID to associate with the uploaded document.
                      If not provided, the PDF filename is used.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {file_path}"
        )

    # 1. Parse PDF into pages
    pages = parse_pdf(str(path))

    # 2. Use provided document ID or fall back to PDF filename
    document_id = document_id or path.name

    # 3. Split pages into chunks
    chunks = chunk_pages(
        pages=pages,
        document_id=document_id,
        source_name=document_id,
    )

    # 4. Store chunks in ChromaDB
    add_chunks(chunks)

    return {
        "status": "ok",
        "name": document_id,
        "chunks": len(chunks),
    }