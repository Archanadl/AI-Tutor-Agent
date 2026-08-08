from fastapi import FastAPI
from pydantic import BaseModel

from app.rag.retriever import run_rag_query


app = FastAPI()


class RAGRequest(BaseModel):
    question: str
    document_id: str


@app.post("/rag/query")
def rag_query(request: RAGRequest):
    return run_rag_query(
        question=request.question,
        document_id=request.document_id
    )