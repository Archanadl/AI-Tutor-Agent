from langchain_core.prompts import PromptTemplate

GRADER_PROMPT = PromptTemplate(
    input_variables=["question", "context"],
    template="""
You are an expert document relevance evaluator for an AI Tutor.

Your task is to determine whether the retrieved context contains enough information to answer the user's question.

Instructions:
1. Read the user's question carefully.
2. Read the retrieved context carefully.
3. Decide whether the context contains sufficient information to answer the question.
4. If sufficient, return:
{{
    "relevant": true
}}
5. Otherwise, return:
{{
    "relevant": false
}}
6. Return ONLY valid JSON.
7. Do NOT include explanations, markdown, code blocks, or any extra text.

User Question:
{question}

Retrieved Context:
{context}
"""
)