from langchain_core.prompts import PromptTemplate

MINDMAP_PROMPT = PromptTemplate(
    input_variables=["topic", "context"],
    template="""
You are an expert educator. Generate a branching concept map as a Mermaid.js flowchart for the given topic.

Topic: {topic}
Context from Study Material:
{context}

STRICT RULES:
1. Use `flowchart TD` as the first line (top-down layout).
2. Every node ID must be a simple alphanumeric string like A, B1, C2 etc.
3. Every node label MUST be wrapped in double quotes inside square brackets: A["Label Here"]
4. NEVER use parentheses, curly braces, or angle brackets for node shapes. ONLY use square brackets with quoted labels.
5. Use --> for connections. Use ---|"label"|--> for labeled edges when helpful.
6. Create 4-6 main branches from the root node.
7. Each main branch should have 2-4 sub-nodes.
8. Sub-nodes can have 1-2 leaf nodes for key details.
9. Add a relevant emoji at the start of each main branch label.
10. Keep labels concise: 1-6 words.
11. Do NOT use any special characters inside labels that could break parsing. No colons, semicolons, backticks, pipes, or unmatched quotes.
12. Return ONLY the raw Mermaid code. No markdown fences, no explanations, no preamble.
13. Use `style` declarations at the end to color the root node distinctly.

Example of CORRECT output format:
flowchart TD
    ROOT["🌐 Web Development"]
    A["🎨 Frontend"]
    B["⚙️ Backend"]
    C["🗄️ Databases"]
    D["🚀 Deployment"]

    ROOT --> A
    ROOT --> B
    ROOT --> C
    ROOT --> D

    A1["HTML and CSS"]
    A2["JavaScript"]
    A3["React or Vue"]
    A --> A1
    A --> A2
    A --> A3

    B1["Node.js"]
    B2["REST APIs"]
    B3["Authentication"]
    B --> B1
    B --> B2
    B --> B3

    C1["SQL Databases"]
    C2["NoSQL Options"]
    C --> C1
    C --> C2

    D1["Docker"]
    D2["CI and CD"]
    D --> D1
    D --> D2

    style ROOT fill:#ff6e6c,stroke:#333,color:#fff,font-weight:bold
""",
)
