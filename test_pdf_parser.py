from app.rag.pdf_parser import parse_pdf


pdf_path = "test_data/research_report.pdf"

pages = parse_pdf(pdf_path)

print("Total pages:", len(pages))

for page in pages[:2]:
    print("\n--- Page ---")
    print("Page number:", page.metadata.get("page"))
    print("Source:", page.metadata.get("source"))
    print("Text:")
    print(page.page_content[:500])