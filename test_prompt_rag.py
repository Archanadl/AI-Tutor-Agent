from app.rag.retriever import retrieve
from app.rag.config import settings
from app.rag.retriever import get_llm
from app.prompts.generator_prompt import GENERATOR_PROMPT


question = "What is the latest version of Java?"
document_id = "test-document-001"

# 1. Retrieve relevant chunks
documents = retrieve(
    question=question,
    document_id=document_id,
    k=3
)

print("\n==============================")
print("RETRIEVED DOCUMENTS")
print("==============================")

for i, doc in enumerate(documents, start=1):
    print(f"\n--- Document {i} ---")
    print("Source:", doc.metadata.get("source"))
    print("Page:", doc.metadata.get("page"))
    print(doc.page_content[:500])


# 2. Build context
context = "\n\n".join(
    doc.page_content
    for doc in documents
)


# 3. Put retrieved context into prompt
prompt = GENERATOR_PROMPT.format(
    context=context,
    question=question
)


print("\n==============================")
print("FINAL PROMPT")
print("==============================")
print(prompt)


# 4. Send prompt to Gemini
llm = get_llm()

response = llm.invoke(prompt)


print("\n==============================")
print("LLM ANSWER")
print("==============================")
print(response.content)