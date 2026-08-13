from pathlib import Path

from app.rag.pdf_parser import parse_pdf
from app.rag.chunker import chunk_pages
from app.rag.vector_store import add_chunks


def ingest_pdf(file_path: str) -> dict:
    """
    Parse a PDF, split it into chunks, and store the chunks in ChromaDB.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    # 1. Parse PDF into pages
    pages = parse_pdf(str(path))

    # 2. Use the PDF filename as the document ID
    document_id = path.name

    # 3. Split pages into chunks
    chunks = chunk_pages(
        pages=pages,
        document_id=document_id,
        source_name=str(path),
    )

    # 4. Store chunks in ChromaDB
    add_chunks(chunks)

    return {
        "status": "ok",
        "name": document_id,
        "chunks": len(chunks),
    }