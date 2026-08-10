# app/graph.py

import os
from typing import TypedDict, List
from langchain_core.documents import Document

# 1. State Definition
class TutorState(TypedDict, total=False):
    student_question: str
    document_id: str
    context: List[Document]
    student_answer: str

# 2. IMPORT MEMBER 2's RAG FUNCTION 
from app.rag.retriever import retrieve

# 3. IMPORT MEMBER 3's PROMPT MANAGER 
from app.prompts.prompt_manager import PromptManager

# ==========================================
# NODES
# ==========================================

def retrieve_node(state: TutorState):
    print("--- RETRIEVING CONTEXT ---")
    question = state.get("student_question", "")
    document_id = state.get("document_id", "")
    
    if not document_id:
        print("WARNING: No document_id found in state. RAG might fail.")
        
    documents = retrieve(
        question=question, 
        document_id=document_id
    )
    
    return {"context": documents}


def generate_node(state: TutorState):
    print("--- GENERATING ANSWER ---")
    question = state.get("student_question", "")
    context = state.get("context", [])
    
    # Temporarily bypassing ChatOpenAI to allow the graph to compile and test
    generator_prompt = PromptManager.get_generator_prompt()
    formatted_prompt = generator_prompt.format(context=context, question=question)    
    # Mocking the response for integration testing
    mock_response = f"This is a mock answer to: '{question}'. The prompt and RAG context formatted successfully!"
    
    return {"student_answer": mock_response}


# ==========================================
# GRAPH DEFINITION
# ==========================================
from langgraph.graph import StateGraph, END

# Initialize the graph
workflow = StateGraph(TutorState)

# Add your updated nodes
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)

# Define the flow
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# Compile it 
tutor_graph = workflow.compile()