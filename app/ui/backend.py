"""Integration boundary between the Streamlit UI and the LangGraph backend.

Response contract
-----------------
{
    "answer": str, "source": str|None, "confidence": float|None,
    "source_type": "RAG"|"WEB"|"NONE", "trace": list[str],
    "agent_status": "completed"|"error",
}
"""

from typing import Any, Dict, List, Optional

USE_REAL_BACKEND = False  # flip to True once the LangGraph app is importable


def _mock(question: str, document: Optional[str]) -> Dict[str, Any]:
    if document is not None:
        return {
            "answer": (
                f"**Mock answer for:** _{question}_\n\n"
                "This response is produced by the UI layer. Once the LangGraph "
                "pipeline is wired in, the retrieved-and-generated answer will "
                "render here with the same source and confidence presentation."
            ),
            "source": document,
            "confidence": 0.92,
            "source_type": "RAG",
            "trace": ["retrieve", "grade", "generate", "done"],
            "agent_status": "completed",
        }
    return {
        "answer": (
            f"**Mock web-fallback answer for:** _{question}_\n\n"
            "No study material is loaded, so the workflow would route to the "
            "web-search tool instead of the local vector store."
        ),
        "source": "duckduckgo.com",
        "confidence": 0.61,
        "source_type": "WEB",
        "trace": ["retrieve", "grade", "web", "generate", "done"],
        "agent_status": "completed",
    }


def ask_tutor(
    question: str,
    chat_history: List[Dict[str, Any]],
    document: Optional[str] = None,
    uploaded_file: Any = None,
) -> Dict[str, Any]:
    """Single entry point the UI uses to talk to the agent system."""
    if not USE_REAL_BACKEND:
        return _mock(question, document)

    try:
        from app.graph.workflow import langgraph_app  # type: ignore

        result = langgraph_app.invoke(
            {
                "question": question,
                "chat_history": chat_history,
                "document": uploaded_file or document,
            }
        )
        return {
            "answer": result.get("answer", ""),
            "source": result.get("source"),
            "confidence": result.get("confidence"),
            "source_type": result.get("source_type", "RAG"),
            "trace": result.get("trace", ["retrieve", "generate", "done"]),
            "agent_status": "completed",
        }
    except Exception as exc:
        return {
            "answer": f"⚠️ The tutor backend is unavailable right now.\n\n`{exc}`",
            "source": None,
            "confidence": None,
            "source_type": "NONE",
            "trace": ["done"],
            "agent_status": "error",
        }


def ingest_document(uploaded_file: Any) -> Dict[str, Any]:
    """Hand an uploaded PDF to the RAG module (Member 2). Mocked for now."""
    if not USE_REAL_BACKEND:
        return {"status": "ok", "chunks": 0, "name": uploaded_file.name}
    from app.rag.ingest import ingest_pdf  # type: ignore

    return ingest_pdf(uploaded_file)


def generate_quiz(topic: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
    """Quiz generation agent hook. Mocked question bank for now."""
    bank = [
        {
            "q": "Which transport-layer protocol is connection-oriented?",
            "options": ["UDP", "TCP", "IP", "HTTP"],
            "answer": "TCP",
            "why": "TCP establishes a connection using the three-way handshake.",
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
            "why": "A DBMS manages storage, retrieval and integrity of data.",
        },
        {
            "q": "Which structure follows FIFO ordering?",
            "options": ["Stack", "Tree", "Queue", "Graph"],
            "answer": "Queue",
            "why": "Queues remove the earliest inserted element first.",
        },
        {
            "q": "Which normal form removes partial dependencies?",
            "options": ["1NF", "2NF", "3NF", "BCNF"],
            "answer": "2NF",
            "why": "2NF requires full functional dependency on the whole key.",
        },
        {
            "q": "Which scheduling policy can starve long jobs?",
            "options": ["FCFS", "Round Robin", "SJF", "Priority ageing"],
            "answer": "SJF",
            "why": "Shortest-Job-First keeps preferring short bursts.",
        },
    ]
    return (bank * ((count // len(bank)) + 1))[:count]
