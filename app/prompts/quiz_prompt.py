from langchain_core.prompts import PromptTemplate

QUIZ_PROMPT = PromptTemplate(
    input_variables=["topic", "difficulty", "count"],
    template="""
You are an expert educational assessor for an AI Tutor.
Your task is to generate a multiple-choice quiz on the following topic:

Topic: {topic}
Difficulty: {difficulty}
Number of questions: {count}

Instructions:
1. Generate exactly {count} multiple-choice questions.
2. The questions should match the requested {difficulty} level.
3. Each question must have exactly 4 options.
4. Provide the correct answer and a brief explanation ("why") for the correct answer.
5. Return ONLY a valid JSON array of objects. Do not include any markdown formatting, code blocks, or conversational text.

The JSON array must strictly follow this structure:
[
  {{
    "q": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option B",
    "why": "Brief explanation of why Option B is correct."
  }},
  ...
]
"""
)
