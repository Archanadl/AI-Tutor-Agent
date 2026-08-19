from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def parse_pdf(file_path: str) -> list[Document]:
    """
    Load a PDF and return one LangChain Document per page.

    Raises:
        FileNotFoundError: If the PDF does not exist.
        ValueError: If the file is not a PDF or contains no extractable text.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {path.suffix}")

    loader = PyPDFLoader(str(path))
    pages = loader.load()

    if not pages:
        raise ValueError(
            f"No extractable text found in {file_path}. "
            "This may be a scanned/image-only PDF that needs OCR."
        )

    for page in pages:
        page.metadata["document_id"] = path.name
        page.metadata["source"] = str(path)

    return pages


def get_pdf_page_count(file_path: str) -> int:
    """
    Return the number of pages containing extracted documents.
    """
    return len(parse_pdf(file_path))