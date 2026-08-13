from app.rag.pdf_parser import parse_pdf
from app.rag.chunker import chunk_pages


pdf_path = "test_data/research_report.pdf"

pages = parse_pdf(pdf_path)

chunks = chunk_pages(
    pages=pages,
    document_id="research_report.pdf",
    source_name="research_report.pdf",
)

print("Original pages:", len(pages))
print("Total chunks:", len(chunks))


for i, chunk in enumerate(chunks[:5]):
    print("\n--- Chunk", i + 1, "---")
    print("Document ID:", chunk.metadata.get("document_id"))
    print("Source:", chunk.metadata.get("source"))
    print("Page:", chunk.metadata.get("page"))
    print("Chunk index:", chunk.metadata.get("chunk_index"))
    print("Characters:", len(chunk.page_content))
    print("Text:", chunk.page_content[:300])