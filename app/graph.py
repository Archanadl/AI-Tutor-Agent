import os
import json
from typing import TypedDict, List

from dotenv import load_dotenv

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

# Check that Groq API key exists
if not os.getenv("GROQ_API_KEY"):
    raise ValueError(
        "GROQ_API_KEY is not set. "
        "Please add GROQ_API_KEY=your_key to the .env file."
    )


# ============================================================
# IMPORTS
# ============================================================

from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from app.rag.retriever import retrieve
from app.prompts.prompt_manager import PromptManager
from mcp_server.web_search_node import web_search_node


# ============================================================
# STATE
# ============================================================

class TutorState(TypedDict, total=False):
    student_question: str
    document_id: str

    # Retrieved study material
    context: List[Document]

    # Grader result
    relevant: bool

    # Final answer
    student_answer: str


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
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

def retrieve_node(state: TutorState):

    print("\n--- RETRIEVING CONTEXT ---")

    question = state.get("student_question", "")
    document_id = state.get("document_id", "")

    if not question:
        print("WARNING: No student question found.")

    if not document_id:
        print("WARNING: No document_id found.")

    documents = retrieve(
        question=question,
        document_id=document_id
    )

    # Make sure context is always a list
    if documents is None:
        documents = []

    print(f"Retrieved documents: {len(documents)}")

    # Print retrieved context for debugging
    for i, document in enumerate(documents, start=1):

        print(f"\nDocument {i}")

        print(
            "Source:",
            document.metadata.get("source", "N/A")
        )

        print(
            "Page:",
            document.metadata.get("page", "N/A")
        )

        print(
            "Relevance score:",
            document.metadata.get(
                "relevance_score",
                "N/A"
            )
        )

        print(
            "Text:",
            document.page_content[:300]
        )

    return {
        "context": documents
    }


# ============================================================
# NODE 2: GRADE RETRIEVED CONTEXT
# ============================================================

def grade_node(state: TutorState):

    print("\n--- GRADING RETRIEVED CONTEXT ---")

    question = state.get("student_question", "")
    context = state.get("context", [])

    # No retrieved context
    if not context:

        print("No context retrieved.")
        print("Relevant: False")

        return {
            "relevant": False
        }

    # Convert documents into plain text
    context_text = "\n\n".join(
        document.page_content
        for document in context
    )

    # Get actual grader prompt
    grader_prompt_template = (
        PromptManager.get_grader_prompt()
    )

    formatted_prompt = grader_prompt_template.format(
        context=context_text,
        question=question
    )

    # Ask LLM to grade retrieved context
    response = llm.invoke(formatted_prompt)

    response_text = extract_text(response)

    print("[GRADER OUTPUT]:")
    print(response_text)

    # Try to parse grader JSON
    try:

        result = json.loads(response_text)

        relevant = bool(
            result.get("relevant", False)
        )

    except (json.JSONDecodeError, AttributeError):

        # Fallback if model doesn't return perfect JSON
        relevant = (
            '"relevant": true'
            in response_text.lower()
        )

    print("Relevant:", relevant)

    return {
        "relevant": relevant
    }


# ============================================================
# NODE 3: GENERATE ANSWER
# ============================================================

def generate_node(state: TutorState):

    print("\n--- GENERATING ANSWER ---")

    question = state.get("student_question", "")
    context = state.get("context", [])

    # Convert retrieved documents to text
    context_text = "\n\n".join(
        document.page_content
        for document in context
    )

    # Get actual generator prompt
    generator_prompt_template = (
        PromptManager.get_generator_prompt()
    )

    formatted_prompt = generator_prompt_template.format(
        context=context_text,
        question=question
    )

    # Generate answer using Groq
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

def route_after_grading(state: TutorState):

    relevant = state.get("relevant", False)

    if relevant:
        return "generate"

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

    print("\n==============================================")
    print("       INITIATING AI TUTOR PIPELINE")
    print("==============================================")

    initial_state = {
    "student_question": "What is quantum computing and what is its time complexity?",
    "document_id": "research_report.pdf"
    }

    final_state = tutor_graph.invoke(
        initial_state
    )

    print("\n==============================================")
    print("           FINAL TUTOR ANSWER")
    print("==============================================")

    print(
        final_state.get(
            "student_answer",
            "No answer generated."
        )
    )

    print("\n==============================================")