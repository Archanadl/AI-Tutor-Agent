from app.rag.retriever import run_rag_query


question = "What is quantum computing?"

document_id = "test-document-001"


result = run_rag_query(
    question=question,
    document_id=document_id,
)


print("\n" + "=" * 60)
print("FINAL RAG RESULT")
print("=" * 60)

print("\nAnswer:")
print(result["answer"])

print("\nSource:")
print(result["source_type"])

print("\nConfidence:")
print(result["confidence_score"])

print("=" * 60)