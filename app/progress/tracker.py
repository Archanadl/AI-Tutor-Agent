"""Progress tracking engine for the AI Tutor."""

from __future__ import annotations

from datetime import datetime, date
from typing import Any, Dict, List, Optional

import streamlit as st


# ============================================================
# INITIALIZATION
# ============================================================

def _ensure_progress_state() -> None:
    """Ensure progress-related session state exists."""

    if "progress_quiz_attempts" not in st.session_state:
        st.session_state.progress_quiz_attempts = []

    if "progress_study_sessions" not in st.session_state:
        st.session_state.progress_study_sessions = []


# ============================================================
# QUIZ TRACKING
# ============================================================

def record_quiz_attempt(
    topic: str,
    difficulty: str,
    score: int,
    total: int,
    questions: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Record one completed quiz attempt.

    Returns the created attempt record.
    """

    _ensure_progress_state()

    percentage = round(
        (score / total) * 100,
        2,
    ) if total > 0 else 0.0

    attempt = {
    "id": f"quiz_{datetime.now().timestamp()}",
    "topic": topic.strip(),
    "difficulty": difficulty,
    "score": score,
    "total": total,
    "percentage": percentage,
    "timestamp": datetime.now().isoformat(),
    "questions": questions or [],
}

    st.session_state.progress_quiz_attempts.append(attempt)

    return attempt


# ============================================================
# STUDY SESSION TRACKING
# ============================================================

def record_study_session(
    session_number: int,
    topics: List[str],
    duration_minutes: int,
) -> Dict[str, Any]:
    """
    Record one completed study-plan session.
    """

    _ensure_progress_state()

    activity = {
        "id": f"study_{datetime.now().timestamp()}",
        "session_number": session_number,
        "topics": topics,
        "duration_minutes": duration_minutes,
        "timestamp": datetime.now().isoformat(),
    }

    st.session_state.progress_study_sessions.append(
        activity
    )

    return activity


# ============================================================
# OVERALL PROGRESS
# ============================================================

def get_progress_summary() -> Dict[str, Any]:
    """Return overall learning statistics."""

    _ensure_progress_state()

    quizzes = st.session_state.progress_quiz_attempts
    sessions = st.session_state.progress_study_sessions

    total_quizzes = len(quizzes)

    average_score = (
        round(
            sum(q["percentage"] for q in quizzes)
            / total_quizzes,
            1,
        )
        if total_quizzes
        else 0.0
    )

    total_study_minutes = sum(
        session.get("duration_minutes", 0)
        for session in sessions
    )

    topics = set()

    for quiz in quizzes:
        if quiz.get("topic"):
            topics.add(quiz["topic"])

    for session in sessions:
        for topic in session.get("topics", []):
            topics.add(topic)

    return {
        "topics_studied": len(topics),
        "quizzes_taken": total_quizzes,
        "average_score": average_score,
        "study_minutes": total_study_minutes,
        "study_hours": round(
            total_study_minutes / 60,
            1,
        ),
    }


# ============================================================
# TOPIC MASTERY
# ============================================================

def get_topic_mastery() -> Dict[str, Dict[str, Any]]:
    """
    Calculate mastery statistics for every topic
    that has quiz attempts.
    """

    _ensure_progress_state()

    quizzes = st.session_state.progress_quiz_attempts

    topic_data: Dict[str, List[float]] = {}

    for quiz in quizzes:

        topic = quiz.get("topic")

        if not topic:
            continue

        if topic not in topic_data:
            topic_data[topic] = []

        topic_data[topic].append(
            quiz.get("percentage", 0)
        )

    mastery = {}

    for topic, scores in topic_data.items():

        average = round(
            sum(scores) / len(scores),
            1,
        )

        latest = scores[-1]
        best = max(scores)

        if average >= 80:
            level = "Strong"
        elif average >= 70:
            level = "Fair"
        else:
            level = "Weak"

        mastery[topic] = {
            "mastery": average,
            "latest_score": latest,
            "best_score": best,
            "attempts": len(scores),
            "level": level,
        }

    return mastery


# ============================================================
# WEAK TOPICS
# ============================================================

def get_weak_topics(
    threshold: float = 70,
) -> List[Dict[str, Any]]:
    """
    Return topics whose average mastery is below
    the supplied threshold.
    """

    mastery = get_topic_mastery()

    weak_topics = []

    for topic, data in mastery.items():

        if data["mastery"] < threshold:

            weak_topics.append(
                {
                    "topic": topic,
                    "mastery": data["mastery"],
                    "attempts": data["attempts"],
                    "level": data["level"],
                }
            )

    weak_topics.sort(
        key=lambda item: item["mastery"]
    )

    return weak_topics


# ============================================================
# STUDY STREAK
# ============================================================

def get_study_streak() -> int:
    """
    Calculate the current consecutive-day study streak.

    A day counts when the user either:
    - completes a study session, or
    - takes a quiz.
    """

    _ensure_progress_state()

    activity_dates = set()

    for quiz in st.session_state.progress_quiz_attempts:

        timestamp = quiz.get("timestamp")

        if timestamp:
            activity_dates.add(
                datetime.fromisoformat(timestamp).date()
            )

    for session in st.session_state.progress_study_sessions:

        timestamp = session.get("timestamp")

        if timestamp:
            activity_dates.add(
                datetime.fromisoformat(timestamp).date()
            )

    if not activity_dates:
        return 0

    today = date.today()

    # If there was no activity today, the current streak is zero.
    if today not in activity_dates:
        return 0

    streak = 0
    current_day = today

    while current_day in activity_dates:

        streak += 1

        current_day = (
            current_day.fromordinal(
                current_day.toordinal() - 1
            )
        )

    return streak


# ============================================================
# RECOMMENDATIONS
# ============================================================

def get_recommendations() -> List[Dict[str, Any]]:
    """
    Generate learning recommendations from weak topics.
    """

    weak_topics = get_weak_topics()

    recommendations = []

    for item in weak_topics:

        topic = item["topic"]
        mastery = item["mastery"]

        recommendations.append(
            {
                "topic": topic,
                "mastery": mastery,
                "message": (
                    f"Review {topic} and take another quiz "
                    f"to improve your current {mastery}% mastery."
                ),
            }
        )

    return recommendations