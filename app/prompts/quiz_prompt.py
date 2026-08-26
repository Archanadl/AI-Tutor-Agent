from langchain_core.prompts import PromptTemplate

QUIZ_PROMPT = PromptTemplate(
    input_variables=["topic", "difficulty", "count"],
    template="""
Generate exactly {count} multiple-choice questions about:

Topic: {topic}
Difficulty: {difficulty}

Return ONLY a valid JSON array. Do NOT include reasoning, <think> tags,
markdown, code fences, explanations outside the JSON, or any other text.

Each question must contain:
- "q": question
- "options": exactly 4 options
- "answer": the correct option
- "why": a short explanation

Keep each question and explanation concise.

Required format:
[
  {{
    "q": "Question?",
    "options": ["A", "B", "C", "D"],
    "answer": "A",
    "why": "Short explanation."
  }}
]
"""
)
