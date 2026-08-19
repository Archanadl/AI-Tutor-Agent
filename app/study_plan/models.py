from dataclasses import dataclass
from typing import List


@dataclass
class StudyTask:
    task_id: str
    topic: str
    description: str
    duration_minutes: int


@dataclass
class StudySession:
    session: int
    tasks: List[StudyTask]
    status: str = "pending"


@dataclass
class StudyPlan:
    goal: str
    current_level: str
    total_sessions: int
    daily_hours: float
    sessions: List[StudySession]