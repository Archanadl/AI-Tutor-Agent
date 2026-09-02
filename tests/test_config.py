from app.rag.config import settings


print("Chunk size:", settings.chunk_size)
print("Chunk overlap:", settings.chunk_overlap)
print("Embedding model:", settings.embedding_model)
print("Chroma collection:", settings.chroma_collection_name)
print("Chroma directory:", settings.chroma_persist_dir)
print("Retrieval k:", settings.retrieval_k)
print("Minimum relevance score:", settings.min_relevance_score)