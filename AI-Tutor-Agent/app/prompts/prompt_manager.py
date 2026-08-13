# Dummy prompt manager for testing
class PromptManager:
    @staticmethod
    def get_grader_prompt():
        return "Based on this context: '{context}', grade if it answers: '{question}'. Reply in JSON: {{\"relevant\": true}}"

    @staticmethod
    def get_generator_prompt():
        return "Based on this context: '{context}', answer the student's question: '{question}'"