from app.prompts.grader_prompt import GRADER_PROMPT
from app.prompts.generator_prompt import GENERATOR_PROMPT
from app.prompts.quiz_prompt import QUIZ_PROMPT

class PromptManager:
    """
    Manages all prompt templates used in the AI Tutor Agent.
    """

    @staticmethod
    def get_grader_prompt():
        return GRADER_PROMPT

    @staticmethod
    def get_generator_prompt():
        return GENERATOR_PROMPT

    @staticmethod
    def get_quiz_prompt():
        return QUIZ_PROMPT

    @staticmethod
    def get_flashcard_prompt():
        from langchain_core.prompts import PromptTemplate
        
        template = """You are an expert educational tutor. Generate {count} high-quality flashcards about the following topic: {topic}.
        
        CRITICAL INSTRUCTION: You MUST return the output strictly as a JSON array of objects. Do not include any greetings, explanations, or markdown formatting (like ```json). 
        
        Each object must have exactly two keys:
        - "front": The question or concept.
        - "back": The concise answer or definition.
        
        Example output format:
        [
            {{"front": "What is polymorphism in Java?", "back": "The ability of different objects to respond to the same method call in their own way."}},
            {{"front": "What is a Stack?", "back": "A Last-In-First-Out (LIFO) data structure."}}
        ]
        """
        return PromptTemplate.from_template(template)