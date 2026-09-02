FLASHCARD_PROMPT = """
You are an AI Tutor creating study flashcards.

Generate exactly {count} flashcards about: {topic}

Each flashcard must contain:
- "front": a clear question or concept
- "back": a concise and correct answer

Return ONLY a valid JSON array.

Example:
[
  {{
    "front": "What is a process in an operating system?",
    "back": "A process is a program in execution."
  }}
]

Topic: {topic}
Number of cards: {count}
"""