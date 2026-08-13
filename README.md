# AI-Tutor-Agent

## Overview

AI Tutor Agent is an intelligent educational assistant developed using Retrieval-Augmented Generation (RAG), LangGraph, and Multi-Component Processing (MCP). The system allows users to upload educational PDF documents, ask questions in natural language, and receive accurate, context-aware responses.

When the required information is unavailable in the uploaded documents, the agent automatically performs a web search and generates an informed response while maintaining conversational context throughout the session.

---

## Problem Statement

Students often spend significant time searching through textbooks, notes, and online resources to find relevant information. This project addresses that challenge by providing an AI-powered tutor capable of answering questions directly from uploaded study materials with an intelligent web search fallback.

---

## Objectives

- Build an AI-powered educational assistant.
- Enable question answering from uploaded PDF documents.
- Implement Retrieval-Augmented Generation (RAG).
- Use LangGraph for workflow orchestration.
- Integrate web search when local documents do not contain relevant information.
- Maintain conversational memory for follow-up questions.

---

## Features

- Upload and process PDF documents
- Intelligent document parsing and chunking
- Semantic search using ChromaDB
- Retrieval-Augmented Generation (RAG)
- Document relevance grading
- Automatic DuckDuckGo web search fallback
- Conversational memory
- Interactive Streamlit chat interface

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| Framework | LangChain, LangGraph |
| Vector Database | ChromaDB |
| Large Language Model | Google Gemini / Groq |
| Web Search | DuckDuckGo |
| MCP Framework | FastMCP |
| Frontend | Streamlit |
| PDF Processing | PyPDF |
| Version Control | Git & GitHub |

---

## Project Structure

```text
AI-Tutor-Agent/
│
├── app/
│   ├── graph/
│   ├── nodes/
│   ├── rag/
│   ├── prompts/
│   ├── tools/
│   ├── memory/
│   ├── ui/
│   └── utils/
│
├── data/
│   ├── pdfs/
│   └── chroma_db/
│
├── docs/
├── tests/
├── assets/
│
├── requirements.txt
├── README.md
├── .env.example
└── main.py
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/<your-username>/AI-Tutor-Agent.git
cd AI-Tutor-Agent
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

**Windows**

```bash
venv\Scripts\activate
```

**macOS/Linux**

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your API key.

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
```

Run the MCP Server (Web Search Tool)

Open a new terminal, activate the environment, and run:

```bash
python -m mcp_server.server
```

Run the application (Frontend)

Open another terminal, activate the environment, and run:

```bash
streamlit run app/ui/app.py
```

---

## Workflow

1. User uploads one or more PDF documents.
2. Documents are parsed and divided into semantic chunks.
3. Chunks are embedded and stored in ChromaDB.
4. User asks a question.
5. The system retrieves the most relevant document chunks.
6. A grading node checks whether the retrieved context is sufficient.
7. If relevant, the LLM generates an answer.
8. Otherwise, the system performs a DuckDuckGo web search using MCP.
9. The final response is generated and returned.
10. Chat history is stored for contextual follow-up questions.

---

## Team Responsibilities

| Member | Responsibility |
|---------|----------------|
| Member 1 | LangGraph architecture and workflow integration |
| Member 2 | PDF parsing, embeddings, and ChromaDB |
| Member 3 | Prompt engineering and evaluation |
| Member 4 | MCP server and web search integration |
| Member 5 | Streamlit frontend development |

---

## Future Enhancements

- Support multiple document collections
- Voice-based interaction
- OCR for scanned PDFs
- Citation-based answers
- User authentication
- Cloud deployment
- Mobile application support

---

## License

This project is developed for educational and research purposes as part of the Dell Technologies GSOP'26.
