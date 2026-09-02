from app.study_plan.planner import generate_study_plan


def test_generate_study_plan():
    plan = generate_study_plan(
        goal="Learn DSA",
        current_level="Beginner",
        topics=[
            "Arrays",
            "Strings",
            "Recursion",
            "Linked List"
        ],
        daily_hours=3,
        duration_days=10,
        plan_type="learning",
        exam_date=None
    )

    assert plan is not None
    assert "study_sessions" in plan

    sessions = plan["study_sessions"]

    assert len(sessions) == 10
    for session in sessions:
        assert session["status"] == "pending"

    for session in sessions:
        assert "session" in session
        assert "tasks" in session
        assert len(session["tasks"]) > 0

        total_minutes = sum(
            task["duration_minutes"]
            for task in session["tasks"]
        )

        assert total_minutes <= 180

def test_generate_exam_preparation_plan():
    plan = generate_study_plan(
        goal="Prepare for DSA test",
        current_level="Beginner",
        topics=[
            "Arrays",
            "Strings",
            "Recursion",
            "Linked List"
        ],
        daily_hours=3,
        duration_days=5,
        plan_type="exam_preparation",
        exam_date="2026-08-25",
    )

    assert plan is not None
    assert "study_sessions" in plan

    sessions = plan["study_sessions"]

    assert len(sessions) == 5

    for session in sessions:
        assert session["status"] == "pending"
        assert "tasks" in session

        total_minutes = sum(
            task["duration_minutes"]
            for task in session["tasks"]
        )

        assert total_minutes <= 180