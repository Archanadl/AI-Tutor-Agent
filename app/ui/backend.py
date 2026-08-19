"""
Integration boundary between the Streamlit UI and the LangGraph backend.

UI
 ↓
backend.py
 ↓
app.graph.tutor_graph
 ↓
Retrieve → Grade → Generate
             ↓
        Web Search (MCP)
"""
from __future__ import annotations

import os
import tempfile
import json
from typing import Any, Dict, List, Optional

# Added spaced repetition import for the flashcard module
from app.rag.spaced_repetition import calculate_sm2 
from app.graph import tutor_graph, llm, extract_text
from app.prompts.prompt_manager import PromptManager
from app.rag.chunker import chunk_pages
from app.rag.pdf_parser import parse_pdf
from app.rag.vector_store import add_chunks
from app.metrics import start_timer, elapsed_ms


# ============================================================
# DOCUMENT INGESTION
# ============================================================

def ingest_document(uploaded_file: Any) -> Dict[str, Any]:
    """
    Save a Streamlit UploadedFile temporarily, parse it,
    chunk it and store the chunks in ChromaDB.
    """

    if uploaded_file is None:
        return {
            "status": "error",
            "chunks": 0,
            "name": None,
            "message": "No file provided.",
        }

    try:
        file_name = uploaded_file.name

        if not file_name.lower().endswith(".pdf"):
            return {
                "status": "error",
                "chunks": 0,
                "name": file_name,
                "message": "Only PDF files are supported.",
            }

        # Save Streamlit UploadedFile temporarily because
        # PyPDFLoader expects a file path.
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:

            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name

        try:
            # ------------------------------------------------
            # 1. Parse PDF
            # ------------------------------------------------
            pages = parse_pdf(temp_path)

            # ------------------------------------------------
            # 2. Chunk PDF
            # ------------------------------------------------
            chunks = chunk_pages(
                pages=pages,
                document_id=file_name,
                source_name=file_name,
            )

            # ------------------------------------------------
            # 3. Store in ChromaDB
            # ------------------------------------------------
            add_chunks(chunks)

            return {
                "status": "ok",
                "chunks": len(chunks),
                "name": file_name,
                "message": f"{len(chunks)} chunks indexed successfully.",
            }

        finally:
            # Remove temporary PDF
            try:
                os.remove(temp_path)
            except OSError:
                pass

    except Exception as exc:
        return {
            "status": "error",
            "chunks": 0,
            "name": getattr(uploaded_file, "name", None),
            "message": str(exc),
        }


# ============================================================
# ASK TUTOR
# ============================================================

def ask_tutor(
    question: str,
    chat_history: List[Dict[str, Any]],
    document: Optional[str] = None,
    uploaded_file: Any = None,
) -> Dict[str, Any]:
    """
    Send a question from the Streamlit UI to the LangGraph tutor agent.
    """

    try:
        # ---------------------------------------------------------
        # Determine document ID
        # ---------------------------------------------------------
        document_id = None

        if uploaded_file is not None:
            document_id = getattr(uploaded_file, "name", None)

        if not document_id and document:
            document_id = document

        # ---------------------------------------------------------
        # Build graph state
        # ---------------------------------------------------------
        state = {
            "student_question": question,
        }

        if document_id:
            state["document_id"] = document_id

        # ---------------------------------------------------------
        # Run LangGraph (timed)
        # ---------------------------------------------------------
        timer = start_timer()

        result = tutor_graph.invoke(state)

        total_ms = elapsed_ms(timer)

        # ---------------------------------------------------------
        # Extract response
        # ---------------------------------------------------------
        answer = result.get(
            "student_answer",
            "No answer was generated.",
        )

        context = result.get("context", [])
        relevance = result.get("relevance", "none")

        # ---------------------------------------------------------
        # Determine source type
        # ---------------------------------------------------------
        if relevance == "full":
            source_type = "RAG"
        elif context:
            source_type = "WEB"
        else:
            source_type = "NONE"

        # ---------------------------------------------------------
        # Extract source
        # ---------------------------------------------------------
        source = None

        if context:
            first_doc = context[0]

            if hasattr(first_doc, "metadata"):
                metadata = first_doc.metadata

                # RAG document source
                source = metadata.get("source")

                # Web-search source
                if source is None:
                    source = metadata.get("url")

        if source is None and source_type == "RAG":
            source = document_id

        # ---------------------------------------------------------
        # Calculate confidence
        # ---------------------------------------------------------
        confidence = None

        if source_type == "RAG" and context:
            scores = []

            for doc in context:
                if hasattr(doc, "metadata"):
                    score = doc.metadata.get("relevance_score")

                    if score is not None:
                        scores.append(float(score))

            if scores:
                confidence = round(sum(scores) / len(scores), 2)

        # ---------------------------------------------------------
        # Execution trace
        # ---------------------------------------------------------
        trace = [
            "retrieve",
            "grade",
        ]

        if source_type == "WEB":
            trace.append("web_search")

        trace.extend([
            "generate",
            "done",
        ])

        return {
            "answer": answer,
            "source": source,
            "confidence": confidence,
            "source_type": source_type,
            "trace": trace,
            "agent_status": "completed",
            "metrics": {
                **result.get("metrics", {}),
                "total_ms": total_ms,
            },
        }

    except Exception as exc:
        return {
            "answer": (
                "⚠️ The tutor backend encountered an error.\n\n"
                f"`{exc}`"
            ),
            "source": None,
            "confidence": None,
            "source_type": "NONE",
            "trace": ["error"],
            "agent_status": "error",
            "metrics": {},
        }


# ============================================================
# QUIZ
# ============================================================

def generate_quiz(
    topic: str,
    difficulty: str,
    count: int,
) -> List[Dict[str, Any]]:

    prompt_template = PromptManager.get_quiz_prompt()
    formatted_prompt = prompt_template.format(
        topic=topic,
        difficulty=difficulty,
        count=count
    )

    try:
        response = llm.invoke(formatted_prompt)
        response_text = extract_text(response).strip()
        
        # Clean up markdown formatting if the LLM wrapped it in ```json ... ```
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
            
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        response_text = response_text.strip()
        
        quiz_data = json.loads(response_text)
        
        if isinstance(quiz_data, list):
            return quiz_data
        else:
            return []
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return []


# ============================================================
# FLASHCARDS
# ============================================================

def get_flashcards(topic: str, count: int = 5) -> List[Dict[str, Any]]:
    """
    Generate flashcards for a specific topic using the LLM.
    Expects the LLM to return a JSON array of front/back card objects.
    """
    # Note: Ensure you have a get_flashcard_prompt() in your PromptManager!
    prompt_template = PromptManager.get_flashcard_prompt()
    formatted_prompt = prompt_template.format(
        topic=topic,
        count=count
    )

    try:
        response = llm.invoke(formatted_prompt)
        response_text = extract_text(response).strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
            
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        response_text = response_text.strip()
        
        flashcard_data = json.loads(response_text)
        
        if isinstance(flashcard_data, list):
            return flashcard_data
        return []
    except Exception as e:
        print(f"Error generating flashcards: {e}")
        return []

def submit_flashcard_answer(
    quality: int, 
    previous_interval: int = 0, 
    previous_repetitions: int = 0, 
    previous_ease_factor: float = 2.5
) -> Dict[str, Any]:
    """
    Process a user's answer to a flashcard and calculate the next review 
    interval using the SM-2 algorithm.
    
    Quality scale (0-5):
    5: Perfect response
    4: Correct response after a hesitation
    3: Correct response recalled with serious difficulty
    2: Incorrect response; where the correct one seemed easy to recall
    1: Incorrect response; the correct one remembered
    0: Complete blackout
    """
    try:
        # Utilize the imported SM-2 function
        new_interval, new_repetitions, new_ease_factor = calculate_sm2(
            quality=quality,
            interval=previous_interval,
            repetitions=previous_repetitions,
            ease_factor=previous_ease_factor
        )
        
        return {
            "status": "success",
            "next_interval_days": new_interval,
            "repetitions": new_repetitions,
            "ease_factor": round(new_ease_factor, 2)
        }
    except Exception as e:
        print(f"Error calculating SM-2: {e}")
        return {
            "status": "error",
            "message": str(e)
        }