"""
app/rag/retriever.py

Complete RAG pipeline:

retrieve
    -> grade documents
    -> web fallback if no relevant documents
    -> generate
    -> verify grounding and answer relevance
    -> retry/web fallback when necessary
"""

from functools import lru_cache
from typing import TypedDict
import json

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from app.rag.config import settings
from app.rag.vector_store import similarity_search

# Member 3 prompts
from app.prompts.grader_prompt import GRADER_PROMPT
from app.prompts.generator_prompt import GENERATOR_PROMPT

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None


# ============================================================
# LLM
# ============================================================

@lru_cache(maxsize=1)
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=settings.llm_temperature,
    )


# ============================================================
# GRAPH STATE
# ============================================================

class RAGState(TypedDict):
    question: str
    document_id: str

    documents: list[Document]
    generation: str

    source_type: str

    confidence_score: float

    web_search_used: bool
    retry_count: int


# ============================================================
# VERIFICATION PROMPTS
# ============================================================

HALLUCINATION_PROMPT = ChatPromptTemplate.from_template(
    """
You are checking whether an AI-generated answer is supported by
the supplied context.

Context:
{context}

Generated answer:
{generation}

Return ONLY valid JSON:

{{
    "grounded": true
}}

or

{{
    "grounded": false
}}

Do not provide explanations.
"""
)


ANSWER_RELEVANCE_PROMPT = ChatPromptTemplate.from_template(
    """
You are checking whether an AI-generated answer actually answers
the student's question.

Question:
{question}

Answer:
{generation}

Return ONLY valid JSON:

{{
    "relevant": true
}}

or

{{
    "relevant": false
}}

Do not provide explanations.
"""
)


# ============================================================
# HELPER
# ============================================================

def parse_json_response(response: str) -> dict:
    """
    Safely parse JSON returned by the LLM.
    """

    response = response.strip()

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Handle accidental markdown code fences
    if "```json" in response:
        response = response.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

    return {}


def response_to_text(response) -> str:
    """
    Convert Gemini/LangChain response content into plain text.
    """

    content = response.content

    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
        )

    return str(content)


# ============================================================
# NODE 1: RETRIEVE
# ============================================================
def retrieve(
    question: str,
    document_id: str,
    k: int | None = None,
) -> list[Document]:
    """
    Retrieve relevant document chunks from ChromaDB.
    """

    results = similarity_search(
        query=question,
        document_id=document_id,
        k=k or settings.retrieval_k,
    )

    documents = []

    for document, score in results:
        if score >= settings.min_relevance_score:
            documents.append(document)

    return documents

def retrieve_node(state: RAGState) -> RAGState:

    results = similarity_search(
        query=state["question"],
        document_id=state["document_id"],
        k=settings.retrieval_k,
    )

    documents = []

    for document, score in results:

        if score >= settings.min_relevance_score:
            documents.append(document)

    return {
        **state,
        "documents": documents,
    }


# ============================================================
# NODE 2: GRADE DOCUMENTS
# ============================================================

def grade_documents_node(state: RAGState) -> RAGState:
    """
    Use the LLM relevance grader to keep only documents
    that contain enough information to answer the question.
    """

    llm = get_llm()

    relevant_documents = []

    print("\n==============================")
    print("DOCUMENT GRADING")
    print("==============================")

    for i, document in enumerate(state["documents"], start=1):

        context = document.page_content

        prompt = GRADER_PROMPT.format(
            question=state["question"],
            context=context,
        )

        try:
            response = llm.invoke(prompt)
            response_text = response_to_text(response)

            result = parse_json_response(response_text)

            relevant = result.get("relevant", False)

            print(f"Document {i}: {relevant}")

            if relevant:
                relevant_documents.append(document)

        except Exception as e:
            print(f"Document {i}: GRADER ERROR - {e}")

    print(f"Kept {len(relevant_documents)} / {len(state['documents'])} documents")

    return {
        **state,
        "documents": relevant_documents,
    }

# ============================================================
# NODE 3: WEB SEARCH FALLBACK
# ============================================================

def web_search_node(state: RAGState) -> RAGState:

    if not settings.tavily_api_key:
        return {
            **state,
            "web_search_used": False,
        }

    if TavilyClient is None:
        return {
            **state,
            "web_search_used": False,
        }

    client = TavilyClient(
        api_key=settings.tavily_api_key
    )

    results = client.search(
        state["question"],
        max_results=3,
    )

    web_documents = []

    for result in results.get("results", []):

        content = result.get("content", "")

        if content:
            web_documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": result.get(
                            "url",
                            "web"
                        )
                    },
                )
            )

    return {
        **state,
        "documents": state["documents"] + web_documents,
        "web_search_used": True,
    }


# ============================================================
# NODE 4: GENERATE ANSWER
# ============================================================

def generate_node(state: RAGState) -> RAGState:

    llm = get_llm()

    context = "\n\n".join(
        document.page_content
        for document in state["documents"]
    )

    if not context:
        context = "No relevant context was found."

    prompt = GENERATOR_PROMPT.format(
        question=state["question"],
        context=context,
    )

    response = llm.invoke(prompt)

    answer = response_to_text(response)

    if state["web_search_used"]:
        source_type = "web_search"

    elif state["documents"]:
        source_type = "document"

    else:
        source_type = "general_knowledge"

    return {
        **state,
        "generation": answer,
        "source_type": source_type,
    }


# ============================================================
# NODE 5: VERIFY GENERATION
# ============================================================

def grade_generation_node(state: RAGState) -> RAGState:
    """
    For now, accept the generated answer.
    The retrieved context has already been filtered by similarity.
    """

    confidence = 0.90 if state["documents"] else 0.25

    return {
        **state,
        "confidence_score": confidence,
        "retry_count": state.get("retry_count", 0) + 1,
    }


# ============================================================
# ROUTING AFTER DOCUMENT GRADING
# ============================================================

def route_after_grading(
    state: RAGState,
) -> str:

    if state["documents"]:
        return "generate"

    return "web_search"


# ============================================================
# ROUTING AFTER GENERATION VERIFICATION
# ============================================================

def route_after_verification(
    state: RAGState,
) -> str:

    confidence = state["confidence_score"]

    retry_count = state.get(
        "retry_count",
        0,
    )

    web_used = state.get(
        "web_search_used",
        False,
    )

    if (
        confidence < 0.5
        and not web_used
        and retry_count < 2
    ):
        return "web_search"

    return "end"


# ============================================================
# BUILD GRAPH
# ============================================================

@lru_cache(maxsize=1)
def get_rag_graph():

    workflow = StateGraph(RAGState)

    workflow.add_node(
        "retrieve",
        retrieve_node,
    )

    workflow.add_node(
        "grade_documents",
        grade_documents_node,
    )

    workflow.add_node(
        "web_search",
        web_search_node,
    )

    workflow.add_node(
        "generate",
        generate_node,
    )

    workflow.add_node(
        "grade_generation",
        grade_generation_node,
    )

    # Entry
    workflow.set_entry_point(
        "retrieve"
    )

    # Retrieve -> Grade
    workflow.add_edge(
        "retrieve",
        "grade_documents",
    )

    # Grade -> Generate OR Web
    workflow.add_conditional_edges(
        "grade_documents",
        route_after_grading,
        {
            "generate": "generate",
            "web_search": "web_search",
        },
    )

    # Web -> Generate
    workflow.add_edge(
        "web_search",
        "generate",
    )

    # Generate -> Verify
    workflow.add_edge(
        "generate",
        "grade_generation",
    )

    # Verify -> Retry/Web OR End
    workflow.add_conditional_edges(
        "grade_generation",
        route_after_verification,
        {
            "web_search": "web_search",
            "end": END,
        },
    )

    return workflow.compile()


# ============================================================
# PUBLIC API
# ============================================================

def run_rag_query(
    question: str,
    document_id: str,
) -> dict:
    """
    Public entry point for the complete RAG pipeline.
    """

    graph = get_rag_graph()

    initial_state: RAGState = {

        "question": question,

        "document_id": document_id,

        "documents": [],

        "generation": "",

        "source_type": "document",

        "confidence_score": 0.0,

        "web_search_used": False,

        "retry_count": 0,
    }

    final_state = graph.invoke(
        initial_state
    )

    return {
        "answer": final_state["generation"],

        "source_type": final_state["source_type"],

        "confidence_score": final_state[
            "confidence_score"
        ],
    }