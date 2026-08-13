import json
import logging
from typing import TypedDict, List

from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from app.rag.retriever import retrieve
from app.prompts.prompt_manager import PromptManager
from app.rag.config import settings
from mcp_server.web_search_node import web_search_node

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


# ============================================================
# LLM
# ============================================================

# Dynamic LLM Initialization based on active configuration
if settings.groq_api_key:
    llm = ChatGroq(
        model=settings.groq_model,
        temperature=settings.llm_temperature,
        api_key=settings.groq_api_key
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

    # Normal LangChain response
    if isinstance(content, str):
        return content

    # Some models may return blocks
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

    question = state.get("student_question", "")
    document_id = state.get("document_id", "")

    if not question:
        logger.warning("No student question found.")

    # No PDF uploaded — skip RAG entirely and let the graph
    # fall through to the MCP web_search node instead of
    # letting retrieve() raise a ValueError.
    if not document_id:
        logger.info("No document_id provided. Skipping RAG retrieval.")
        return {
            "context": []
        }

    documents = retrieve(
        question=question,
        document_id=document_id
    )

    # Make sure context is always a list
    if documents is None:
        documents = []

    logger.info("Retrieved documents: %d", len(documents))

    # Log retrieved context for debugging
    for i, document in enumerate(documents, start=1):
        logger.debug(
            "Document %d | Source: %s | Page: %s | Score: %s",
            i,
            document.metadata.get("source", "N/A"),
            document.metadata.get("page", "N/A"),
            document.metadata.get("relevance_score", "N/A")
        )
        logger.debug("Text: %s...", document.page_content[:300])

    return {
        "context": documents
    }


# ============================================================
# NODE 2: GRADE RETRIEVED CONTEXT
# ============================================================

def grade_node(state: TutorState) -> dict:

    logger.info("--- GRADING RETRIEVED CONTEXT ---")

    question = state.get("student_question", "")
    context = state.get("context", [])

    # No retrieved context
    if not context:
        logger.info("No context retrieved. Relevance: none")
        return {
            "relevance": "none"
        }

    # Convert documents into plain text
    context_text = "\n\n".join(
        document.page_content
        for document in context
    )

    # Get grader prompt
    grader_prompt_template = PromptManager.get_grader_prompt()

    formatted_prompt = grader_prompt_template.format(
        context=context_text,
        question=question
    )

    # Ask LLM to grade retrieved context
    response = llm.invoke(formatted_prompt)
    response_text = extract_text(response).strip()

    logger.debug("[GRADER OUTPUT]: %s", response_text)

    # Parse grader JSON
    try:
        result = json.loads(response_text)
        relevance = result.get("relevance", "none").lower()

    except (json.JSONDecodeError, AttributeError):
        logger.warning(
            "Could not parse grader response: %s",
            response_text
        )
        relevance = "none"

    # Validate grader output
    if relevance not in {"full", "partial", "none"}:
        logger.warning(
            "Invalid relevance value '%s'. Treating as none.",
            relevance
        )
        relevance = "none"

    logger.info("Relevance: %s", relevance)

    return {
        "relevance": relevance
    }


# ============================================================
# NODE 3: GENERATE ANSWER
# ============================================================

def generate_node(state: TutorState) -> dict:

    logger.info("--- GENERATING ANSWER ---")

    question = state.get("student_question", "")
    context = state.get("context", [])

    # Convert retrieved documents to text
    context_text = "\n\n".join(
        document.page_content
        for document in context
    )

    logger.info("Context length provided to LLM: %d chars", len(context_text))
    if context_text:
        logger.debug("Context snippet: %s...", context_text[:100])

    # Get actual generator prompt
    generator_prompt_template = (
        PromptManager.get_generator_prompt()
    )

    formatted_prompt = generator_prompt_template.format(
        context=context_text,
        question=question
    )

    # Generate answer using LLM
    response = llm.invoke(formatted_prompt)
    answer = extract_text(response)

    return {
        "student_answer": answer
    }


# ============================================================
# NODE 4: WEB SEARCH (MCP)
# ============================================================
# The actual implementation lives in mcp_server/web_search_node.py.
# It connects to the local FastMCP server (port 8000), performs a
# DuckDuckGo search, and appends the results to state["context"]
# so the generate node can use them to answer the student.


# ============================================================
# CONDITIONAL ROUTING
# ============================================================

def route_after_grading(state: TutorState) -> str:

    relevance = state.get("relevance", "none")

    if relevance == "full":
        return "generate"

    # Partial or none → use web search
    return "web_search"


# ============================================================
# BUILD LANGGRAPH
# ============================================================

workflow = StateGraph(TutorState)


# Add nodes
workflow.add_node(
    "retrieve",
    retrieve_node
)

workflow.add_node(
    "grade",
    grade_node
)

workflow.add_node(
    "generate",
    generate_node
)

workflow.add_node(
    "web_search",
    web_search_node
)


# ============================================================
# DEFINE FLOW
# ============================================================

# Start
workflow.set_entry_point("retrieve")


# Retrieve → Grade
workflow.add_edge(
    "retrieve",
    "grade"
)


# Grade → Generate OR Fallback
workflow.add_conditional_edges(
    "grade",
    route_after_grading,
    {
        "generate": "generate",
        "web_search": "web_search"
    }
)


# Generate → End
workflow.add_edge(
    "generate",
    END
)


# Web Search → Generate (so the LLM answers using web results)
workflow.add_edge(
    "web_search",
    "generate"
)


# ============================================================
# COMPILE GRAPH
# ============================================================

tutor_graph = workflow.compile()


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    logger.info("INITIATING AI TUTOR PIPELINE")

    initial_state = {
        "student_question": "What is quantum computing and what is its time complexity?",
        "document_id": "research_report.pdf",
    }

    final_state = tutor_graph.invoke(initial_state)

    print("\n" + "=" * 46)
    print("           FINAL TUTOR ANSWER")
    print("=" * 46)

    print(
        final_state.get(
            "student_answer",
            "No answer generated."
        )
    )

    print("\n==============================================")