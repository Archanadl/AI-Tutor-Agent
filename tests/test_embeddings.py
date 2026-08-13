from app.rag.embeddings import embed_query


query = "What is quantum computing?"

vector = embed_query(query)

print("Embedding generated successfully!")
print("Vector size:", len(vector))
print("First 5 values:", vector[:5])