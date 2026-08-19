from dataclasses import dataclass
from typing import List


@dataclass
class StudyTask:
    task_id: str
    topic: str
    description: str
    duration_minutes: int


@dataclass
class StudyDay:
    day: int
    tasks: List[StudyTask]


@dataclass
class StudyPlan:
    goal: str
    current_level: str
    duration_days: int
    daily_hours: float
    days: List[StudyDay]