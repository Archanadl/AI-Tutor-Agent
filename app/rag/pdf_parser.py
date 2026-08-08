"""
app/rag/pdf_parser.py

Responsible only for getting text OUT of a PDF, page by page. Deliberately
does not chunk or embed anything — that's chunker.py's and embeddings.py's
job respectively. Keeping this boundary clean means you can swap the PDF
library (e.g. for OCR support on scanned PDFs) without touching anything
downstream.
"""

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def parse_pdf(file_path: str) -> list[Document]:
    """
    Loads a PDF and returns one LangChain Document per page, with page
    number already attached in metadata (PyPDFLoader sets this automatically).

    Raises FileNotFoundError if the path doesn't exist, and ValueError if
    the PDF has no extractable text (e.g. a scanned image PDF with no OCR).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {path.suffix}")

    loader = PyPDFLoader(str(path))
    pages = loader.load()

    if not pages or all(not p.page_content.strip() for p in pages):
        raise ValueError(
            f"No extractable text found in {file_path}. "
            "This may be a scanned/image-only PDF that needs OCR."
        )

    return pages


def get_pdf_page_count(file_path: str) -> int:
    """
    Return the number of pages containing extracted documents.
    """
    return len(parse_pdf(file_path))