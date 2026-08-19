import json
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

  
def validate_input(
    goal: str,
    current_level: str,
    topics: list[str],
    daily_hours: float,
    duration_days: int
):
    """
    Validate the information required to create
    a flexible personalized study plan.

    duration_days represents the number of study sessions,
    not calendar days.
    """

    if not goal or not goal.strip():
        raise ValueError("Goal cannot be empty.")

    if not current_level or not current_level.strip():
        raise ValueError("Current level cannot be empty.")

    if not topics:
        raise ValueError("At least one topic is required.")

    cleaned_topics = [
        topic.strip()
        for topic in topics
        if topic.strip()
    ]

    if not cleaned_topics:
        raise ValueError("At least one valid topic is required.")

    if daily_hours <= 0:
        raise ValueError(
            "Available study time must be greater than 0."
        )

    if duration_days <= 0:
        raise ValueError(
            "Number of study sessions must be greater than 0."
        )

    return {
        "goal": goal.strip(),
        "current_level": current_level.strip(),
        "topics": cleaned_topics,
        "daily_hours": daily_hours,
        "duration_days": duration_days
    }
STUDY_PLAN_PROMPT = """
You are an expert personalized study-plan generator.

Create a realistic and flexible study plan for a student based on the information below.

Goal:
{goal}

Current level:
{current_level}

Topics:
{topics}

Available study time per study session:
{daily_hours} hours

Number of study sessions:
{duration_days}

IMPORTANT SCHEDULING RULES:
1. The number of study sessions must be exactly {duration_days}.
2. "Study session" does NOT mean a calendar day.
3. The student can complete study sessions whenever they want.
4. The student does NOT have to study on consecutive calendar days.
5. Never assign calendar dates such as Monday, Tuesday, or specific dates.
6. If the student skips a calendar day, no study session is lost.
7. The plan represents learning sessions, not a fixed calendar schedule.
8. Each study session should fit within the available study time.
9. Distribute the provided topics in a logical learning order.
10. Start from the student's current level.
11. Keep each study session concise and realistic.
12. Prefer 2 or 3 tasks per study session.
13. Include learning, practice, and revision where appropriate.
14. Make the plan practical and achievable.
15. Do not introduce completely unrelated topics.
16. Return ONLY valid JSON.
17. Do not include reasoning, explanations, Markdown, or code fences.
18. Start the response directly with {{ and end it with }}.

Each study session should have:
- A session number
- One or more tasks
- A topic for each task
- A description
- Duration in minutes

The total duration of the tasks in each session must NOT exceed
{daily_hours} hours.

Return exactly this structure:

{{
    "study_sessions": [
        {{
            "session": 1,
            "tasks": [
                {{
                    "topic": "topic name",
                    "description": "what the student should do",
                    "duration_minutes": 60
                }}
            ]
        }}
    ]
}}
"""
if not os.getenv("GROQ_API_KEY"):
    raise ValueError(
        "GROQ_API_KEY is not set. Please check your .env file."
    )
llm = ChatGroq(
    model="qwen/qwen3.6-27b",
    temperature=0.7,
    reasoning_effort="none"
)
def generate_study_plan(
    goal: str,
    current_level: str,
    topics: list[str],
    daily_hours: float,
    duration_days: int
):
    """
    Generate a personalized study plan using Groq.
    """

    validated = validate_input(
        goal=goal,
        current_level=current_level,
        topics=topics,
        daily_hours=daily_hours,
        duration_days=duration_days
    )

    prompt = STUDY_PLAN_PROMPT.format(
        goal=validated["goal"],
        current_level=validated["current_level"],
        topics=", ".join(validated["topics"]),
        daily_hours=validated["daily_hours"],
        duration_days=validated["duration_days"]
    )

    response = llm.invoke(prompt)

    print("\n========== RAW LLM RESPONSE ==========")
    print(repr(response.content))
    print("======================================\n")

    response_text = response.content

    # Remove accidental Markdown code fences
    if response_text.startswith("```"):
        response_text = response_text.replace("```json", "")
        response_text = response_text.replace("```", "")
        response_text = response_text.strip()

    try:
        plan = json.loads(response_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The LLM returned invalid JSON."
        ) from error

    # Initialize every generated study session as pending.
    for session in plan.get("study_sessions", []):
        session["status"] = "pending"

    return plan
def complete_session(plan: dict, session_number: int) -> dict:
    """
    Mark a study session as completed.

    Sessions are independent of calendar dates.
    Skipping a day does not affect the plan.
    """

    sessions = plan.get("study_sessions", [])

    for session in sessions:
        if session.get("session") == session_number:
            session["status"] = "completed"
            return plan

    raise ValueError(
        f"Study session {session_number} does not exist."
    )
def start_session(plan: dict, session_number: int) -> dict:
    """
    Mark a study session as in progress.
    """

    sessions = plan.get("study_sessions", [])

    for session in sessions:
        if session.get("session") == session_number:
            if session.get("status", "pending") == "completed":
                raise ValueError(
                    f"Study session {session_number} is already completed."
                )

            session["status"] = "in_progress"
            return plan

    raise ValueError(
        f"Study session {session_number} does not exist."
    )


def get_next_pending_session(plan: dict):
    """
    Return the first study session whose status is pending.
    """

    sessions = plan.get("study_sessions", [])

    for session in sessions:
        if session.get("status", "pending") == "pending":
            return session

    return None
def get_study_plan_progress(plan: dict) -> dict:
    """
    Return the current progress of a flexible study plan.
    """

    sessions = plan.get("study_sessions", [])

    total_sessions = len(sessions)

    completed_sessions = sum(
        1
        for session in sessions
        if session.get("status", "pending") == "completed"
    )

    in_progress_sessions = [
        session["session"]
        for session in sessions
        if session.get("status", "pending") == "in_progress"
    ]

    next_pending = get_next_pending_session(plan)

    return {
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "remaining_sessions": total_sessions - completed_sessions,
        "in_progress_session": (
            in_progress_sessions[0]
            if in_progress_sessions
            else None
        ),
        "next_pending_session": (
            next_pending["session"]
            if next_pending
            else None
        )
    }