from app.rag.pdf_parser import parse_pdf
from app.rag.chunker import chunk_pages
from app.rag.vector_store import add_chunks, similarity_search


# 1. Parse PDF
pdf_path = "test_data/research_report.pdf"
pages = parse_pdf(pdf_path)

print("Pages:", len(pages))


# 2. Create chunks
chunks = chunk_pages(
    pages,
    document_id="test-document-001",
    source_name="research_report.pdf"
)

print("Chunks:", len(chunks))


# 3. Store chunks in ChromaDB
add_chunks(chunks)

print("Chunks stored successfully!")


# 4. Test similarity search
results = similarity_search(
    "What is quantum computing?",
    document_id="test-document-001",
    k=3
)

print("\n--- Search Results ---")

for i, (document, score) in enumerate(results, start=1):
    print(f"\nResult {i}")
    print("Score:", score)
    print("Page:", document.metadata.get("page"))
    print("Source:", document.metadata.get("source"))
    print("Text:", document.page_content[:300])