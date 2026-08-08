from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    chroma_collection_name: str = "ai_tutor"
    chroma_persist_dir: str = "./chroma_db"

    retrieval_k: int = 4
    min_relevance_score: float = 0.3

    google_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    llm_temperature: float = 0.0
    tavily_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
