from langchain_core.prompts import PromptTemplate

GRADER_PROMPT = PromptTemplate(
    input_variables=["question", "context"],
    template="""
You are an expert document relevance evaluator for an AI Tutor.

Your task is to evaluate whether the retrieved context contains enough information to answer the user's question.

Instructions:

1. Read the user question carefully and identify all information required to answer it.

2. Read the retrieved context carefully.

3. Compare the information required by the question with the information available in the retrieved context.

4. Classify the retrieved context into exactly one of these categories:

   * "full": The retrieved context contains sufficient information to answer the entire question.
   * "partial": The retrieved context contains sufficient information to answer only part of the question, but some information required by the question is missing.
   * "none": The retrieved context does not contain sufficient relevant information to answer the question.

5. Use only the retrieved context when making the classification.

6. Do not use outside knowledge to fill missing information.

7. If the question contains multiple parts, evaluate whether the context covers all required parts.

8. A context should be classified as "full" only when the retrieved information is sufficient for the complete question.

9. If even an important part of the question cannot be answered from the retrieved context, classify it as "partial".

10. If the question is unrelated to the retrieved context, classify it as "none".

11. Return ONLY valid JSON.

12. Do NOT include explanations, reasoning, markdown, code blocks, or any extra text.

13. The "relevance" value MUST be exactly one of:
    "full", "partial", or "none".

Return exactly one JSON object:

{{
    "relevance": "full"
}}

OR

{{
    "relevance": "partial"
}}

OR

{{
    "relevance": "none"
}}

User Question:
{question}

Retrieved Context:
{context}
"""
)