from app.rag.retriever import retrieve


question = "What is quantum computing?"

documents = retrieve(
    question=question,
    document_id="research_report.pdf",
    k=3,
)

print("Retrieved documents:", len(documents))

for i, document in enumerate(documents, start=1):
    print(f"\n--- Result {i} ---")

    print("Source:", document.metadata.get("source"))
    print("Page:", document.metadata.get("page"))
    print("Document ID:", document.metadata.get("document_id"))
    print("Chunk:", document.metadata.get("chunk_index"))
    print(
        "Relevance Score:",
        document.metadata.get("relevance_score")
    )

    print("Text:")
    print(document.page_content[:500])