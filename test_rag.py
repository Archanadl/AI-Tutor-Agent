from app.rag.retriever import run_rag_query

result = run_rag_query(
    "What is quantum computing?",
    "test-document-001"
)

print("Answer:", result["answer"])
print("Source:", result["source_type"])
print("Confidence:", result["confidence_score"])