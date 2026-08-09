from app.rag.retriever import get_rag_graph


question = "What is quantum computing?"
document_id = "test-document-001"

graph = get_rag_graph()

initial_state = {
    "question": question,
    "document_id": document_id,
    "documents": [],
    "generation": "",
    "source_type": "document",
    "confidence_score": 0.0,
    "web_search_used": False,
    "retry_count": 0,
}

result = graph.invoke(initial_state)

print("\n==============================")
print("FINAL RESULT")
print("==============================")

print("Retrieved/graded documents:", len(result["documents"]))

for i, doc in enumerate(result["documents"], start=1):
    print(f"\nDocument {i}")
    print("Source:", doc.metadata.get("source"))
    print("Page:", doc.metadata.get("page"))
    print("Text:", doc.page_content[:300])

print("\nAnswer:")
print(result["generation"])