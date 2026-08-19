import json
import logging
from typing import TypedDict, List, Optional

from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from app.rag.retriever import retrieve, generate_flashcards
from app.prompts.prompt_manager import PromptManager
from app.rag.config import settings
from mcp_server.web_search_node import web_search_node
from app.metrics import start_timer, elapsed_ms, create_metrics

# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )


# ============================================================
# STATE
# ============================================================

class TutorState(TypedDict, total=False):
    student_question: str
    document_id: str

    # Retrieved study material
    context: List[Document]

    # Grader result: "full" | "partial" | "none"
    relevance: str

    # Final answer
    student_answer: str

    # Per-node timing (ms)
    metrics: dict

    # --- FLASHCARD MODULE FIELDS ---
    mode: str                          # "qa" | "generate_flashcards" | "grade_flashcard"
    topic: str                         # Topic for flashcards
    pending_flashcards: List[dict]     # List of newly generated cards
    current_flashcard: dict            # The specific card currently being answered
    current_user_answer: str           # User's typed response to the flashcard
    flashcard_score: int               # Score (0-5)
    flashcard_feedback: str            # AI feedback on user's answer


# ============================================================
# LLM
# ============================================================

# Dynamic LLM Initialization based on active configuration
if settings.groq_api_key:
    llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)
    
elif settings.google_api_key:
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        temperature=settings.llm_temperature,
        google_api_key=settings.google_api_key
    )
else:
    raise ValueError(
        "No API key provided. Please set either GOOGLE_API_KEY or GROQ_API_KEY in your .env file."
    )


# ============================================================
# HELPER: EXTRACT TEXT FROM LLM RESPONSE
# ============================================================

def extract_text(response):
    """
    Handles different response formats returned by the LLM.
    """
    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict):
                text_parts.append(block.get("text", ""))
        return "".join(text_parts)

    return str(content)


# ============================================================
# NODE 1: RETRIEVE
# ============================================================

def retrieve_node(state: TutorState) -> dict:
    logger.info("--- RETRIEVING CONTEXT ---")
    timer = start_timer()

    question = state.get("student_question", "")
    document_id = state.get("document_id", "")

    if not question:
        logger.warning("No student question found.")

    if not document_id:
        logger.info("No document_id provided. Skipping RAG retrieval.")
        return {
            "context": [],
            "metrics": {
                **state.get("metrics", create_metrics()),
                "retrieve_ms": elapsed_ms(timer),
            },
        }

    documents = retrieve(
        question=question,
        document_id=document_id
    )

    if documents is None:
        documents = []

    logger.info("Retrieved documents: %d", len(documents))

    return {
        "context": documents,
        "metrics": {
            **state.get("metrics", create_metrics()),
            "retrieve_ms": elapsed_ms(timer),
        },
    }


# ============================================================
# NODE 2: GRADE RETRIEVED CONTEXT
# ============================================================

def grade_node(state: TutorState) -> dict:
    logger.info("--- GRADING RETRIEVED CONTEXT ---")
    timer = start_timer()

    question = state.get("student_question", "")
    context = state.get("context", [])

    if not context:
        logger.info("No context retrieved. Relevance: none")
        return {
            "relevance": "none",
            "metrics": {
                **state.get("metrics", create_metrics()),
                "grade_ms": elapsed_ms(timer),
            },
        }

    context_text = "\n\n".join(document.page_content for document in context)
    grader_prompt_template = PromptManager.get_grader_prompt()

    formatted_prompt = grader_prompt_template.format(
        context=context_text,
        question=question
    )

    response = llm.invoke(formatted_prompt)
    response_text = extract_text(response).strip()

    logger.debug("[GRADER OUTPUT]: %s", response_text)

    try:
        result = json.loads(response_text)
        relevance = result.get("relevance", "none").lower()
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Could not parse grader response: %s", response_text)
        relevance = "none"

    if relevance not in {"full", "partial", "none"}:
        logger.warning("Invalid relevance value '%s'. Treating as none.", relevance)
        relevance = "none"

    logger.info("Relevance: %s", relevance)

    return {
        "relevance": relevance,
        "metrics": {
            **state.get("metrics", create_metrics()),
            "grade_ms": elapsed_ms(timer),
        },
    }


# ============================================================
# NODE 3: GENERATE ANSWER
# ============================================================

def generate_node(state: TutorState) -> dict:
    logger.info("--- GENERATING ANSWER ---")
    timer = start_timer()

    question = state.get("student_question", "")
    context = state.get("context", [])

    context_text = "\n\n".join(document.page_content for document in context)
    generator_prompt_template = PromptManager.get_generator_prompt()

    formatted_prompt = generator_prompt_template.format(
        context=context_text,
        question=question
    )

    response = llm.invoke(formatted_prompt)
    answer = extract_text(response)

    return {
        "student_answer": answer,
        "metrics": {
            **state.get("metrics", create_metrics()),
            "generate_ms": elapsed_ms(timer),
        },
    }


# ============================================================
# NODE 5: GENERATE FLASHCARDS (NEW)
# ============================================================

def generate_flashcards_node(state: TutorState) -> dict:
    logger.info("--- GENERATING FLASHCARDS ---")
    timer = start_timer()

    topic = state.get("topic") or state.get("student_question", "General Study")
    document_id = state.get("document_id", "")

    # Calls the logic in app/rag/retriever.py
    cards = generate_flashcards(topic=topic, document_id=document_id)

    return {
        "pending_flashcards": cards,
        "metrics": {
            **state.get("metrics", create_metrics()),
            "flashcard_gen_ms": elapsed_ms(timer),
        },
    }


# ============================================================
# NODE 6: GRADE FLASHCARD ANSWER (NEW)
# ============================================================

def grade_flashcard_node(state: TutorState) -> dict:
    logger.info("--- GRADING FLASHCARD ANSWER ---")
    timer = start_timer()

    card = state.get("current_flashcard", {})
    user_answer = state.get("current_user_answer", "")

    prompt = f"""
    You are an AI Tutor grading a student's flashcard response.
    
    Flashcard Question: {card.get('front', '')}
    Correct Answer: {card.get('back', '')}
    Student's Answer: {user_answer}

    Evaluate the student's answer and return ONLY a JSON object:
    {{
      "score": <integer from 0 to 5, where 0=completely wrong, 3=partially correct, 5=perfect>,
      "feedback": "<one short concise sentence explaining the grade>"
    }}
    """

    response = llm.invoke(prompt)
    resp_text = extract_text(response).strip()

    # Clean markdown fences if LLM wrapped output
    if "```json" in resp_text:
        resp_text = resp_text.split("```json")[1].split("```")[0].strip()
    elif "```" in resp_text:
        resp_text = resp_text.split("```")[1].split("```")[0].strip()

    try:
        grade_data = json.loads(resp_text)
        score = int(grade_data.get("score", 0))
        feedback = grade_data.get("feedback", "Evaluation complete.")
    except Exception:
        logger.warning("Could not parse grade JSON: %s", resp_text)
        score = 3
        feedback = "Evaluated response."

    return {
        "flashcard_score": score,
        "flashcard_feedback": feedback,
        "metrics": {
            **state.get("metrics", create_metrics()),
            "flashcard_grade_ms": elapsed_ms(timer),
        },
    }


# ============================================================
# CONDITIONAL ROUTING
# ============================================================

def route_entry_point(state: TutorState) -> str:
    """Routes based on the requested execution mode."""
    mode = state.get("mode", "qa")
    if mode == "generate_flashcards":
        return "generate_flashcards"
    elif mode == "grade_flashcard":
        return "grade_flashcard"
    return "retrieve"


def route_after_grading(state: TutorState) -> str:
    relevance = state.get("relevance", "none")
    if relevance == "full":
        return "generate"
    return "web_search"


# ============================================================
# BUILD LANGGRAPH
# ============================================================

workflow = StateGraph(TutorState)

# Add existing nodes
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("grade", grade_node)
workflow.add_node("generate", generate_node)
workflow.add_node("web_search", web_search_node)

# Add flashcard nodes
workflow.add_node("generate_flashcards", generate_flashcards_node)
workflow.add_node("grade_flashcard", grade_flashcard_node)

# Dynamic Entry Point
workflow.set_conditional_entry_point(
    route_entry_point,
    {
        "retrieve": "retrieve",
        "generate_flashcards": "generate_flashcards",
        "grade_flashcard": "grade_flashcard",
    }
)

# Standard QA Flow
workflow.add_edge("retrieve", "grade")
workflow.add_conditional_edges(
    "grade",
    route_after_grading,
    {
        "generate": "generate",
        "web_search": "web_search"
    }
)
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

# Flashcard Flow Endpoints
workflow.add_edge("generate_flashcards", END)
workflow.add_edge("grade_flashcard", END)

# ============================================================
# COMPILE GRAPH
# ============================================================

tutor_graph = workflow.compile()


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":
    logger.info("INITIATING AI TUTOR PIPELINE")

    # Test 1: Standard Q&A
    initial_state = {
        "mode": "qa",
        "student_question": "What is quantum computing and what is its time complexity?",
        "document_id": "research_report.pdf",
    }
    final_state = tutor_graph.invoke(initial_state)
    print("\n" + "=" * 46)
    print("           FINAL TUTOR ANSWER")
    print("=" * 46)
    print(final_state.get("student_answer", "No answer generated."))
    print("\nMetrics:", final_state.get("metrics"))

    # Test 2: Test Flashcard Grading Node
    test_flashcard_state = {
        "mode": "grade_flashcard",
        "current_flashcard": {
            "front": "What is supervised learning?",
            "back": "Learning from labeled training data."
        },
        "current_user_answer": "It is machine learning where we train on labeled examples."
    }
    flashcard_result = tutor_graph.invoke(test_flashcard_state)
    print("\n" + "=" * 46)
    print("           FLASHCARD GRADE TEST")
    print("=" * 46)
    print(f"Score: {flashcard_result.get('flashcard_score')}/5")
    print(f"Feedback: {flashcard_result.get('flashcard_feedback')}")