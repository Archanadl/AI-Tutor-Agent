# AI-Tutor-Agent

## Overview

AI Tutor Agent is an intelligent educational assistant built with Retrieval-Augmented Generation (RAG), LangGraph, and a modern full-stack architecture. Users can upload educational PDF documents, ask questions in natural language, generate flashcards, take quizzes, visualize mind maps, and create personalized study plans — all powered by Google Gemini and Groq LLMs.

When the required information is unavailable in the uploaded documents, the agent automatically performs a web search (via DuckDuckGo through an MCP server) and generates an informed response while maintaining conversational context throughout the session.

---

## Features

- **PDF Upload & RAG** — Upload study materials; the agent chunks, embeds, and retrieves relevant content semantically
- **AI Chat Tutor** — Ask questions grounded in your uploaded documents, with automatic web search fallback
- **Mind Maps** — Generate interactive, branched mind maps visualized with Mermaid.js (zoom, pan, fullscreen, SVG download)
- **Flashcards** — AI-generated flashcards with spaced-repetition scheduling (SM-2 algorithm)
- **Quizzes** — Topic-based quizzes with configurable difficulty and question count
- **Study Plans** — Personalized multi-session study plans with progress tracking
- **Web Search Fallback** — Automatic DuckDuckGo search when documents lack relevant context
- **Theming** — Multiple UI themes (Midnight Aurora, Forest Deep, Solar Flare, Light Frost)

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.13, TypeScript |
| AI / LLM | Google Gemini, Groq |
| Agent Framework | LangChain, LangGraph |
| Vector Database | ChromaDB |
| Web Search | DuckDuckGo (via MCP server) |
| MCP Framework | FastMCP |
| Backend API | FastAPI + Uvicorn |
| Frontend | React 19, Vite, TypeScript |
| Diagramming | Mermaid.js |
| PDF Processing | PyPDF |
| Version Control | Git & GitHub |

---

## Project Structure

```text
AI-Tutor-Agent/
│
├── app/
│   ├── api/
│   │   └── main.py            # FastAPI backend (REST API)
│   ├── graph.py               # LangGraph workflow definition
│   ├── prompts/               # LLM prompt templates
│   │   ├── mindmap_prompt.py
│   │   ├── flashcard_prompt.py
│   │   ├── quiz_prompt.py
│   │   ├── grader_prompt.py
│   │   ├── generator_prompt.py
│   │   └── prompt_manager.py
│   ├── rag/                   # RAG pipeline (chunking, embeddings, retrieval)
│   ├── study_plan/            # Study plan generation logic
│   ├── progress/              # Session progress tracking
│   ├── ui/
│   │   └── backend.py         # Core business logic (shared with FastAPI)
│   └── metrics.py
│
├── frontend/                  # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/          # AI chat interface
│   │   │   ├── mindmap/       # Mind map viewer
│   │   │   ├── flashcards/    # Flashcard UI
│   │   │   └── studyplan/     # Study plan UI
│   │   ├── App.tsx
│   │   └── index.css          # Theme system & design tokens
│   └── vite.config.ts
│
├── mcp_server/
│   ├── server.py              # MCP server entry point
│   └── web_search_node.py     # DuckDuckGo web search tool
│
├── chroma_db/                 # Persistent vector store
├── requirements.txt
├── .env.example
└── main.py
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/AI-Tutor-Agent.git
cd AI-Tutor-Agent
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example file and fill in your API keys:

```bash
cp .env.example .env
```

```env
GOOGLE_API_KEY=your_google_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

> Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/) and your Groq key from [console.groq.com](https://console.groq.com/).

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Running the Application

The app requires **three processes** running concurrently. Open three separate terminal tabs/windows, activate the virtual environment in each, and run:

### Terminal 1 — MCP Web Search Server

```bash
source .venv/bin/activate
python -m mcp_server.server
```

### Terminal 2 — FastAPI Backend

```bash
source .venv/bin/activate
uvicorn app.api.main:app --reload --port 8000
```

> API available at `http://localhost:8000`  
> Interactive API docs at `http://localhost:8000/docs`

### Terminal 3 — React Frontend

```bash
cd frontend
npm run dev
```

> Web UI available at **`http://localhost:5173`**

The Vite dev server proxies all `/api` requests to the FastAPI backend automatically.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload a PDF document |
| `POST` | `/api/chat` | Send a question to the AI tutor |
| `POST` | `/api/flashcards` | Generate flashcards for a topic |
| `POST` | `/api/flashcards/submit` | Submit a flashcard answer (SM-2 scheduling) |
| `POST` | `/api/quiz` | Generate a quiz |
| `POST` | `/api/study-plan` | Create a personalized study plan |
| `POST` | `/api/study-plan/session/start` | Begin a study session |
| `POST` | `/api/study-plan/session/complete` | Complete a study session |
| `POST` | `/api/study-plan/progress` | Get study plan progress |
| `POST` | `/api/mindmap` | Generate a mind map (returns Mermaid code) |

---

## Workflow

1. User uploads a PDF document via the frontend.
2. The document is parsed, chunked, embedded, and stored in ChromaDB.
3. User asks a question in the Chat view.
4. The LangGraph agent retrieves the most relevant chunks from ChromaDB.
5. A grading node checks whether retrieved context is sufficient.
6. If relevant, the LLM generates a grounded answer.
7. If not, the MCP server performs a DuckDuckGo web search and the LLM synthesizes the result.
8. The response is returned with conversational memory maintained.

---

## Future Enhancements

- Voice-based interaction
- OCR support for scanned PDFs
- Citation-based answers with source highlighting
- User authentication & multi-user support
- Cloud deployment (GCP / AWS)
- Mobile application

---

## License

This project is developed for educational and research purposes as part of the Dell Technologies GSOP'26.
