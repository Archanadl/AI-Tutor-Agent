"""
app/rag/retriever.py

Retrieves the most relevant chunks from ChromaDB
for a user's question.
"""
from langchain_core.documents import Document

# These imports assume your teammates have created these files!
from app.rag.vector_store import similarity_search
from app.rag.config import settings

# ---> ADD ANY IMPORTS YOUR FLASHCARD LOGIC NEEDS HERE <---
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
# Assuming your team uses OpenAI via LangChain. 
# Change to ChatGoogleGenerativeAI or ChatAnthropic if your team uses a different provider.
from langchain_openai import ChatOpenAI 

def retrieve(
    question: str,
    document_id: str,
    k: int | None = None,
) -> list[Document]:
    """
    Retrieve the most relevant document chunks for a question.
    """
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not document_id:
        raise ValueError("document_id cannot be empty.")

    results = similarity_search(
        query=question,
        document_id=document_id,
        k=k if k is not None else settings.retrieval_k,
    )

    documents = []

    for document, score in results:
        if score >= settings.min_relevance_score:
            document.metadata["relevance_score"] = score
            documents.append(document)

    return documents

# ---------------------------------------------------------
# --- YOUR FLASHCARD LOGIC BELOW ---
# ---------------------------------------------------------

# 1. Enforce Structured Output
class Flashcard(BaseModel):
    front: str = Field(description="The clear, atomic question or concept to test.")
    back: str = Field(description="The concise, correct answer.")

class FlashcardSet(BaseModel):
    cards: List[Flashcard] = Field(description="A list of exactly 5 generated flashcards.")

def generate_flashcards(topic: str, document_id: str) -> list[dict]:
    """
    Generates a set of spaced-repetition ready flashcards based on a topic.
    Uses the team's existing RAG retrieval to ground the LLM's knowledge.
    """
    # Step 1: Use the existing function above to get relevant course material
    # We use the topic as the "question" to pull the most relevant chunks
    retrieved_docs = retrieve(question=topic, document_id=document_id, k=5)
    
    # Combine the retrieved text chunks into one context string
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    if not context_text:
        return [] # No context found, return empty or handle error
        
    # Step 2: Initialize your LLM and bind the Pydantic schema
    # (Check app/rag/config.py to see how your team initializes the LLM!)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    structured_llm = llm.with_structured_output(FlashcardSet)
    
    # Step 3: Prompt the LLM
    prompt = f"""
    You are an expert AI Tutor. Create exactly 5 highly effective flashcards 
    based on the following course material about the topic: '{topic}'.
    
    Keep the front (question) atomic, and the back (answer) concise and accurate.
    
    Course Material:
    {context_text}
    """
    
    # Generate the structured response
    result = structured_llm.invoke(prompt)
    
    # Step 4: Attach your SM-2 baseline metrics to the generated cards
    flashcards_with_metrics = []
    for index, card in enumerate(result.cards):
        flashcards_with_metrics.append({
            "id": f"card_{int(datetime.now().timestamp())}_{index}", # Unique ID for the DB
            "topic": topic,
            "front": card.front,
            "back": card.back,
            "repetitions": 0,          # SM-2 baseline
            "interval": 0,             # SM-2 baseline
            "ease_factor": 2.5,        # SM-2 baseline
            "next_review_date": datetime.now().isoformat()
        })
        
    return flashcards_with_metrics