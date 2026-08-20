import streamlit as st
from app.progress.tracker import get_study_streak
from app.progress.tracker import (
    record_quiz_attempt,
    record_study_session,
    get_progress_summary,
    get_topic_mastery,
    get_weak_topics,
    get_recommendations,
    get_study_streak,
)


def clear_state():
    st.session_state.clear()


def test_quiz_attempt_is_recorded():

    clear_state()

    record_quiz_attempt(
        topic="Computer Networks",
        difficulty="Medium",
        score=4,
        total=5,
    )

    summary = get_progress_summary()

    assert summary["quizzes_taken"] == 1
    assert summary["average_score"] == 80.0


def test_topic_mastery():

    clear_state()

    record_quiz_attempt(
        topic="Computer Networks",
        difficulty="Medium",
        score=4,
        total=5,
    )

    mastery = get_topic_mastery()

    assert "Computer Networks" in mastery
    assert mastery["Computer Networks"]["mastery"] == 80.0
    assert mastery["Computer Networks"]["level"] == "Strong"


def test_weak_topic():

    clear_state()

    record_quiz_attempt(
        topic="DBMS",
        difficulty="Easy",
        score=2,
        total=5,
    )

    weak_topics = get_weak_topics()

    assert len(weak_topics) == 1
    assert weak_topics[0]["topic"] == "DBMS"
    assert weak_topics[0]["mastery"] == 40.0


def test_recommendation():

    clear_state()

    record_quiz_attempt(
        topic="Operating Systems",
        difficulty="Medium",
        score=2,
        total=5,
    )

    recommendations = get_recommendations()

    assert len(recommendations) == 1
    assert recommendations[0]["topic"] == "Operating Systems"
    assert "Review Operating Systems" in recommendations[0]["message"]


def test_study_session():

    clear_state()

    record_study_session(
        session_number=1,
        topics=["Arrays", "Strings"],
        duration_minutes=60,
    )

    summary = get_progress_summary()

    assert summary["topics_studied"] == 2
    assert summary["study_minutes"] == 60
    assert summary["study_hours"] == 1.0

def test_study_streak():

    clear_state()

    record_study_session(
        session_number=1,
        topics=["Arrays"],
        duration_minutes=30,
    )

    streak = get_study_streak()

    assert streak == 1