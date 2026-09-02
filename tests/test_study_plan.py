import pytest

from app.study_plan.planner import validate_input


def test_valid_input():
    result = validate_input(
        goal="Learn DSA",
        current_level="Beginner",
        topics=["Arrays", "Strings", "Recursion"],
        daily_hours=3,
        duration_days=10
    )

    assert result["goal"] == "Learn DSA"
    assert result["current_level"] == "Beginner"
    assert len(result["topics"]) == 3
    assert result["daily_hours"] == 3
    assert result["duration_days"] == 10


def test_empty_goal():
    with pytest.raises(ValueError):
        validate_input(
            goal="",
            current_level="Beginner",
            topics=["Arrays"],
            daily_hours=3,
            duration_days=10
        )


def test_empty_topics():
    with pytest.raises(ValueError):
        validate_input(
            goal="Learn DSA",
            current_level="Beginner",
            topics=[],
            daily_hours=3,
            duration_days=10
        )


def test_invalid_daily_hours():
    with pytest.raises(ValueError):
        validate_input(
            goal="Learn DSA",
            current_level="Beginner",
            topics=["Arrays"],
            daily_hours=0,
            duration_days=10
        )


def test_invalid_duration():
    with pytest.raises(ValueError):
        validate_input(
            goal="Learn DSA",
            current_level="Beginner",
            topics=["Arrays"],
            daily_hours=3,
            duration_days=0
        )