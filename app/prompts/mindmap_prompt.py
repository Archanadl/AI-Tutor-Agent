from langchain_core.prompts import PromptTemplate

MINDMAP_PROMPT = PromptTemplate(
    input_variables=["topic", "context"],
    template="""
You are an expert AI Tutor. Your task is to generate a comprehensive mind map using Mermaid.js syntax.

Topic: {topic}
Context from Study Material:
{context}

Instructions:
1. Generate a mind map representing the key concepts, sub-concepts, and relationships related to the Topic.
2. If Context from Study Material is provided, use it as the primary source of information for the mind map. If it is empty or insufficient, use your general knowledge about the Topic.
3. The output MUST be valid Mermaid.js `mindmap` syntax.
4. Start the code with `mindmap` on the first line. Do not use Markdown code blocks (e.g., ```mermaid). Just the raw Mermaid text.
5. Use indentation to show hierarchy (root node, branches, sub-branches). Use spaces, not tabs, for indentation.
6. Keep node labels concise (1-5 words).
7. Return ONLY the Mermaid code.

Example structure:
mindmap
  Root Node
    Branch 1
      Sub-branch 1.1
      Sub-branch 1.2
    Branch 2
      Sub-branch 2.1
"""
)
