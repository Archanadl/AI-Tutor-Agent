from app.study_plan.planner import (
    complete_session,
    get_next_pending_session,
    get_study_plan_progress,
    start_session,
)

def create_test_plan():
    return {
        "study_sessions": [
            {
                "session": 1,
                "status": "pending",
                "tasks": []
            },
            {
                "session": 2,
                "status": "pending",
                "tasks": []
            },
            {
                "session": 3,
                "status": "pending",
                "tasks": []
            }
        ]
    }


def test_complete_session():
    plan = create_test_plan()

    complete_session(plan, 1)

    assert plan["study_sessions"][0]["status"] == "completed"


def test_next_pending_session():
    plan = create_test_plan()

    complete_session(plan, 1)

    next_session = get_next_pending_session(plan)

    assert next_session["session"] == 2


def test_skipping_days_does_not_change_session():
    plan = create_test_plan()

    # Student completes Session 1.
    complete_session(plan, 1)

    # No function is called for the next calendar day.
    # Session 2 must remain pending.
    assert plan["study_sessions"][1]["status"] == "pending"


def test_all_sessions_completed():
    plan = create_test_plan()

    complete_session(plan, 1)
    complete_session(plan, 2)
    complete_session(plan, 3)

    assert get_next_pending_session(plan) is None
def test_start_session():
    plan = create_test_plan()

    start_session(plan, 1)

    assert plan["study_sessions"][0]["status"] == "in_progress"
def test_cannot_start_completed_session():
    plan = create_test_plan()

    complete_session(plan, 1)

    try:
        start_session(plan, 1)
        assert False, "Expected ValueError"
    except ValueError:
        assert True
def test_study_plan_progress():
    plan = create_test_plan()

    # Initially all 3 sessions are pending.
    progress = get_study_plan_progress(plan)

    assert progress["total_sessions"] == 3
    assert progress["completed_sessions"] == 0
    assert progress["remaining_sessions"] == 3
    assert progress["in_progress_session"] is None
    assert progress["next_pending_session"] == 1

    # Start Session 1.
    start_session(plan, 1)

    progress = get_study_plan_progress(plan)

    assert progress["in_progress_session"] == 1
    assert progress["next_pending_session"] == 2

    # Complete Session 1.
    complete_session(plan, 1)

    progress = get_study_plan_progress(plan)

    assert progress["total_sessions"] == 3
    assert progress["completed_sessions"] == 1
    assert progress["remaining_sessions"] == 2
    assert progress["in_progress_session"] is None
    assert progress["next_pending_session"] == 2