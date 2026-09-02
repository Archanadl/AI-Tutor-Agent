from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import app.ui.backend as backend

app = FastAPI(title="AI Tutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    chat_history: List[Dict[str, Any]]
    document_id: Optional[str] = None

class FlashcardRequest(BaseModel):
    topic: str
    count: int = 5

class FlashcardSubmitRequest(BaseModel):
    quality: int
    previous_interval: int = 0
    previous_repetitions: int = 0
    previous_ease_factor: float = 2.5

class QuizRequest(BaseModel):
    topic: str
    difficulty: str
    count: int

class StudyPlanRequest(BaseModel):
    goal: str
    current_level: str
    topics: List[str]
    daily_hours: float
    duration_days: int
    plan_type: str = "learning"
    exam_date: Optional[str] = None

class StudySessionRequest(BaseModel):
    plan: Dict[str, Any]
    session_number: int

class MindmapRequest(BaseModel):
    topic: str
    document_id: Optional[str] = None


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    # Streamlit UploadedFile has slightly different API than FastAPI UploadFile
    # We will mock it to make backend.py happy
    class MockUploadedFile:
        def __init__(self, name, content):
            self.name = name
            self._content = content
        def getvalue(self):
            return self._content

    content = await file.read()
    mock_file = MockUploadedFile(file.filename, content)
    result = backend.ingest_document(mock_file)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@app.post("/api/chat")
async def chat(request: ChatRequest):
    result = backend.ask_tutor(
        question=request.question,
        chat_history=request.chat_history,
        document=request.document_id,
    )
    return result

@app.post("/api/quiz")
async def generate_quiz(request: QuizRequest):
    result = backend.generate_quiz(
        topic=request.topic,
        difficulty=request.difficulty,
        count=request.count,
    )
    return {"quiz": result}

@app.post("/api/flashcards")
async def generate_flashcards(request: FlashcardRequest):
    result = backend.get_flashcards(
        topic=request.topic,
        count=request.count,
    )
    return {"flashcards": result}

@app.post("/api/flashcards/submit")
async def submit_flashcard(request: FlashcardSubmitRequest):
    result = backend.submit_flashcard_answer(
        quality=request.quality,
        previous_interval=request.previous_interval,
        previous_repetitions=request.previous_repetitions,
        previous_ease_factor=request.previous_ease_factor,
    )
    return result

@app.post("/api/study-plan")
async def create_study_plan(request: StudyPlanRequest):
    result = backend.create_study_plan(
        goal=request.goal,
        current_level=request.current_level,
        topics=request.topics,
        daily_hours=request.daily_hours,
        duration_days=request.duration_days,
        plan_type=request.plan_type,
        exam_date=request.exam_date,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/study-plan/session/start")
async def start_study_session(request: StudySessionRequest):
    result = backend.begin_study_session(request.plan, request.session_number)
    return result

@app.post("/api/study-plan/session/complete")
async def complete_study_session(request: StudySessionRequest):
    result = backend.finish_study_session(request.plan, request.session_number)
    return result

@app.post("/api/study-plan/progress")
async def get_study_plan_progress(request: StudySessionRequest):
    # Actually get_study_plan_status takes just the plan
    result = backend.get_study_plan_status(request.plan)
    return result

@app.post("/api/mindmap")
async def create_mindmap(request: MindmapRequest):
    result = backend.generate_mindmap(
        topic=request.topic,
        document_id=request.document_id,
    )
    return {"code": result}
