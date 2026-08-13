"""
Integration boundary between the Streamlit UI and the LangGraph backend.

UI
 ↓
backend.py
 ↓
app.graph.tutor_graph
 ↓
Retrieve → Grade
             ↓
        ┌────┴────┐
        ↓         ↓
     Generate   Web Search (MCP)
                  ↓
               Generate
"""

from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, List, Optional

from app.graph import tutor_graph
from app.rag.chunker import chunk_pages
from app.rag.pdf_parser import parse_pdf
from app.rag.vector_store import add_chunks


# ============================================================
# BACKEND MODE
# ============================================================

# Real LangGraph + RAG + MCP backend is enabled.
USE_REAL_BACKEND = True


# ============================================================
# DOCUMENT INGESTION
# ============================================================

def ingest_document(uploaded_file: Any) -> Dict[str, Any]:
    """
    Ingest a Streamlit UploadedFile into ChromaDB.

    Pipeline:
        UploadedFile
            ↓
        Temporary PDF
            ↓
        PDF parser
            ↓
        Chunking
            ↓
        ChromaDB

    Returns:
        {
            "status": "ok" | "error",
            "chunks": int,
            "name": str | None,
            "message": str
        }
    """

    if uploaded_file is None:
        return {
            "status": "error",
            "chunks": 0,
            "name": None,
            "message": "No file provided.",
        }

    temp_path = None

    try:
        file_name = uploaded_file.name

        # ----------------------------------------------------
        # Validate file type
        # ----------------------------------------------------

        if not file_name.lower().endswith(".pdf"):
            return {
                "status": "error",
                "chunks": 0,
                "name": file_name,
                "message": "Only PDF files are supported.",
            }

        # ----------------------------------------------------
        # Save uploaded file temporarily
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name

        # ----------------------------------------------------
        # 1. Parse PDF
        # ----------------------------------------------------

        pages = parse_pdf(temp_path)

        if not pages:
            return {
                "status": "error",
                "chunks": 0,
                "name": file_name,
                "message": "No readable text was found in the PDF.",
            }

        # ----------------------------------------------------
        # 2. Chunk PDF
        # ----------------------------------------------------

        chunks = chunk_pages(
            pages=pages,
            document_id=file_name,
            source_name=file_name,
        )

        if not chunks:
            return {
                "status": "error",
                "chunks": 0,
                "name": file_name,
                "message": "No chunks could be created from the PDF.",
            }

        # ----------------------------------------------------
        # 3. Store chunks in ChromaDB
        # ----------------------------------------------------

        add_chunks(chunks)

        return {
            "status": "ok",
            "chunks": len(chunks),
            "name": file_name,
            "message": f"{len(chunks)} chunks indexed successfully.",
        }

    except Exception as exc:
        return {
            "status": "error",
            "chunks": 0,
            "name": getattr(uploaded_file, "name", None),
            "message": str(exc),
        }

    finally:
        # ----------------------------------------------------
        # Remove temporary PDF
        # ----------------------------------------------------

        if temp_path:
            try:
                os.remove(temp_path)
            except OSError:
                pass


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
    Send a student question from the Streamlit UI to LangGraph.

    Current graph state expects:

        student_question
        document_id

    The graph handles:

        PDF available
            ↓
        RAG retrieval
            ↓
        Grader
            ↓
        Generate

        OR

        No relevant RAG context
            ↓
        MCP Web Search
            ↓
        Generate

        OR

        No PDF
            ↓
        Skip RAG retrieval
            ↓
        Web Search
            ↓
        Generate
    """

    if not USE_REAL_BACKEND:
        return _mock(question, document)

    try:
        # ----------------------------------------------------
        # Validate question
        # ----------------------------------------------------

        if not question or not question.strip():
            return {
                "answer": "Please enter a question.",
                "source": None,
                "confidence": None,
                "source_type": "NONE",
                "trace": [],
                "agent_status": "error",
            }

        # ----------------------------------------------------
        # Determine document ID
        # ----------------------------------------------------

        document_id = document or ""

        if uploaded_file is not None:
            document_id = uploaded_file.name

        # ----------------------------------------------------
        # Invoke LangGraph
        # ----------------------------------------------------

        result = tutor_graph.invoke(
            {
                "student_question": question,
                "document_id": document_id,
            }
        )

        # ----------------------------------------------------
        # Extract final answer
        # ----------------------------------------------------

        answer = result.get(
            "student_answer",
            "I couldn't generate an answer.",
        )

        # ----------------------------------------------------
        # Determine source
        # ----------------------------------------------------

        context = result.get("context", []) or []

        source_type = "RAG" if document_id else "WEB"
        source = document_id if document_id else None

        web_sources = []
        rag_sources = []

        for doc in context:
            metadata = getattr(doc, "metadata", {}) or {}

            source_value = metadata.get("source")

            if not source_value:
                continue

            source_value = str(source_value)

            if (
                source_value.startswith("http://")
                or source_value.startswith("https://")
            ):
                web_sources.append(source_value)
            else:
                rag_sources.append(source_value)

        # ----------------------------------------------------
        # MCP / Web search detection
        # ----------------------------------------------------

        if web_sources:
            source_type = "WEB"
            source = web_sources[0]

        elif rag_sources:
            source_type = "RAG"
            source = rag_sources[0]

        # ----------------------------------------------------
        # Build pipeline trace
        # ----------------------------------------------------

        trace = [
            "retrieve",
            "grade",
        ]

        if source_type == "WEB":
            trace.append("web")

        trace.extend(
            [
                "generate",
                "done",
            ]
        )

        # ----------------------------------------------------
        # Calculate confidence
        # ----------------------------------------------------

        confidence = None

        relevance_scores = []

        for doc in context:
            metadata = getattr(doc, "metadata", {}) or {}

            score = metadata.get("relevance_score")

            if isinstance(score, (int, float)):
                relevance_scores.append(float(score))

        if relevance_scores:
            confidence = max(
                0.0,
                min(
                    1.0,
                    sum(relevance_scores)
                    / len(relevance_scores),
                ),
            )

        # ----------------------------------------------------
        # Return UI response contract
        # ----------------------------------------------------

        return {
            "answer": answer,
            "source": source,
            "confidence": confidence,
            "source_type": source_type,
            "trace": trace,
            "agent_status": "completed",
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
            "trace": ["done"],
            "agent_status": "error",
        }


# ============================================================
# MOCK BACKEND
# ============================================================

def _mock(
    question: str,
    document: Optional[str],
) -> Dict[str, Any]:
    """
    Mock response retained for local UI testing if needed.
    """

    if document:
        return {
            "answer": (
                f"**Mock answer for:** _{question}_\n\n"
                "This response is produced by the UI layer."
            ),
            "source": document,
            "confidence": 0.92,
            "source_type": "RAG",
            "trace": [
                "retrieve",
                "grade",
                "generate",
                "done",
            ],
            "agent_status": "completed",
        }

    return {
        "answer": (
            f"**Mock web-fallback answer for:** _{question}_\n\n"
            "No study material is loaded."
        ),
        "source": "duckduckgo.com",
        "confidence": 0.61,
        "source_type": "WEB",
        "trace": [
            "retrieve",
            "grade",
            "web",
            "generate",
            "done",
        ],
        "agent_status": "completed",
    }


# ============================================================
# QUIZ
# ============================================================

def generate_quiz(
    topic: str,
    difficulty: str,
    count: int,
) -> List[Dict[str, Any]]:
    """
    Temporary quiz question bank.

    This can later be replaced with the quiz-generation agent
    without changing the UI interface.
    """

    bank = [
        {
            "q": "Which transport-layer protocol is connection-oriented?",
            "options": [
                "UDP",
                "TCP",
                "IP",
                "HTTP",
            ],
            "answer": "TCP",
            "why": (
                "TCP establishes a connection using "
                "the three-way handshake."
            ),
        },
        {
            "q": "What does DBMS stand for?",
            "options": [
                "Database Management System",
                "Data Backup Management System",
                "Database Machine System",
                "Data Management Software",
            ],
            "answer": "Database Management System",
            "why": (
                "A DBMS manages storage, retrieval "
                "and integrity of data."
            ),
        },
        {
            "q": "Which structure follows FIFO ordering?",
            "options": [
                "Stack",
                "Tree",
                "Queue",
                "Graph",
            ],
            "answer": "Queue",
            "why": (
                "Queues remove the earliest inserted "
                "element first."
            ),
        },
        {
            "q": "Which normal form removes partial dependencies?",
            "options": [
                "1NF",
                "2NF",
                "3NF",
                "BCNF",
            ],
            "answer": "2NF",
            "why": (
                "2NF requires full functional dependency "
                "on the whole key."
            ),
        },
        {
            "q": "Which scheduling policy can starve long jobs?",
            "options": [
                "FCFS",
                "Round Robin",
                "SJF",
                "Priority ageing",
            ],
            "answer": "SJF",
            "why": (
                "Shortest-Job-First keeps preferring "
                "short bursts."
            ),
        },
    ]

    if count <= 0:
        return []

    return (bank * ((count // len(bank)) + 1))[:count]