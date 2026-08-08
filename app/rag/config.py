class Settings:
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_collection_name: str = "ai_tutor"
    chroma_persist_dir: str = "chroma_db"

    retrieval_k: int = 4
    min_relevance_score: float = 0.3
settings = Settings()
