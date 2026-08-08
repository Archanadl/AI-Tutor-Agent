from app.rag.retriever import retrieve


question = "What is quantum computing?"

documents = retrieve(
    question=question,
    document_id="test-document-001",
    k=3,
)

print("Retrieved documents:", len(documents))

for i, document in enumerate(documents, start=1):
    print(f"\n--- Result {i} ---")

    print("Source:", document.metadata.get("source"))
    print("Page:", document.metadata.get("page"))
    print("Chunk:", document.metadata.get("chunk_index"))

    print("Text:")
    print(document.page_content[:500])