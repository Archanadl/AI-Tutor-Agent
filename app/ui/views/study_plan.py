"""Study plan view — personalized learning and exam preparation plans."""

from datetime import date, timedelta

import streamlit as st

from components import hero, spacer

from backend import (
    create_study_plan,
    begin_study_session,
    finish_study_session,
)


def render():
    hero(
        eyebrow="Planner agent",
        title="A study plan shaped around your",
        highlight="goal and available time.",
        subtitle=(
            "Create a flexible study plan that you can complete "
            "consecutively or whenever you have time."
        ),
    )

    spacer(24)

    # =========================================================
    # CREATE STUDY PLAN
    # =========================================================

    st.subheader("🎯 Create your personalized study plan")

    plan_type = st.selectbox(
        "📚 Plan type",
        ["Learning", "Exam Preparation"],
    )

    goal = st.text_input(
        "🎯 What do you want to achieve?",
        placeholder="Example: Learn DSA for placement preparation",
    )

    current_level = st.selectbox(
        "📊 Current level",
        ["Beginner", "Intermediate", "Advanced"],
    )

    topics_text = st.text_input(
        "📖 Topics",
        placeholder="Example: Arrays, Strings, Recursion, Linked List",
    )

    col1, col2 = st.columns(2)

    with col1:
        hours = st.slider(
            "⏱️ Study time per session (hours)",
            min_value=1.0,
            max_value=8.0,
            value=3.0,
            step=0.5,
        )

    with col2:
        duration_sessions = st.number_input(
            "🔢 Number of study sessions",
            min_value=1,
            max_value=365,
            value=10,
            step=1,
        )

    # Exam date is required only for exam preparation
    exam_date = None

    if plan_type == "Exam Preparation":
        exam_date = st.date_input(
            "📅 Exam date",
            value=date.today() + timedelta(days=7),
        )

    st.caption(
        "Your plan contains study sessions, not fixed calendar days. "
        "You can complete sessions consecutively or whenever you have time. "
        "Skipping a day does not remove a session."
    )

    generate_plan = st.button(
        "✨ Generate Personalized Study Plan",
        type="primary",
    )

    # =========================================================
    # GENERATE PLAN
    # =========================================================

    if generate_plan:

        if not goal.strip():
            st.error("Please enter your study goal.")

        elif not topics_text.strip():
            st.error("Please enter at least one topic.")

        else:

            topics = [
                topic.strip()
                for topic in topics_text.split(",")
                if topic.strip()
            ]

            try:

                plan = create_study_plan(
                    goal=goal,
                    current_level=current_level,
                    topics=topics,
                    daily_hours=hours,
                    duration_days=int(duration_sessions),
                    plan_type=(
                        "exam_preparation"
                        if plan_type == "Exam Preparation"
                        else "learning"
                    ),
                    exam_date=(
                        exam_date.isoformat()
                        if exam_date is not None
                        else None
                    ),
                )

                # ---------------------------------------------
                # Check backend error
                # ---------------------------------------------

                if "error" in plan:

                    st.error(
                        f"Could not generate study plan: "
                        f"{plan['error']}"
                    )

                # ---------------------------------------------
                # Validate generated sessions
                # ---------------------------------------------

                elif not plan.get("study_sessions"):

                    st.error(
                        "The planner returned no study sessions."
                    )

                else:

                    # Store valid plan
                    st.session_state["study_plan"] = plan

                    st.success(
                        "✅ Personalized study plan generated successfully!"
                    )

            except Exception as exc:

                st.error(
                    f"Could not generate study plan: {exc}"
                )

    # =========================================================
    # DISPLAY GENERATED STUDY PLAN
    # =========================================================

    plan = st.session_state.get("study_plan")

    if not plan:
        return

    spacer(28)

    st.subheader("📖 Your Study Plan")

    sessions = plan.get(
        "study_sessions",
        [],
    )

    if not sessions:

        st.warning(
            "No study sessions were generated."
        )

        return

    # =========================================================
    # PROGRESS SUMMARY
    # =========================================================

    completed_count = sum(
        1
        for session in sessions
        if session.get("status") == "completed"
    )

    in_progress = [
        session
        for session in sessions
        if session.get("status") == "in_progress"
    ]

    remaining_count = len(sessions) - completed_count

    progress = completed_count / len(sessions)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Sessions",
            len(sessions),
        )

    with col2:
        st.metric(
            "Completed",
            completed_count,
        )

    with col3:
        st.metric(
            "Remaining",
            remaining_count,
        )

    st.progress(
        progress,
        text=(
            f"{completed_count} of "
            f"{len(sessions)} sessions completed"
        ),
    )

    spacer(20)

    # =========================================================
    # STUDY SESSIONS
    # =========================================================

    for session in sessions:

        session_number = session.get(
            "session"
        )

        status = session.get(
            "status",
            "pending",
        )

        tasks = session.get(
            "tasks",
            [],
        )

        total_minutes = sum(
            task.get(
                "duration_minutes",
                0,
            )
            for task in tasks
        )

        # -----------------------------------------------------
        # Status
        # -----------------------------------------------------

        if status == "completed":

            status_icon = "✅"
            status_text = "Completed"

        elif status == "in_progress":

            status_icon = "🟡"
            status_text = "In progress"

        else:

            status_icon = "⬜"
            status_text = "Pending"

        # -----------------------------------------------------
        # Session
        # -----------------------------------------------------

        with st.container(border=True):

            st.markdown(
                f"### {status_icon} Session {session_number}"
            )

            st.caption(
                f"{status_text} · "
                f"{total_minutes} minutes"
            )

            # -------------------------------------------------
            # Tasks
            # -------------------------------------------------

            for task in tasks:

                topic = task.get(
                    "topic",
                    "Study topic",
                )

                description = task.get(
                    "description",
                    "",
                )

                duration = task.get(
                    "duration_minutes",
                    0,
                )

                st.markdown(
                    f"**{topic}** — {duration} min"
                )

                if description:

                    st.caption(
                        description
                    )

            spacer(8)

            # -------------------------------------------------
            # Session actions
            # -------------------------------------------------

            if status == "pending":

                if st.button(
                    f"▶️ Start Session {session_number}",
                    key=f"start_session_{session_number}",
                ):

                    try:

                        begin_study_session(
                            plan,
                            session_number,
                        )

                        st.session_state[
                            "study_plan"
                        ] = plan

                        st.rerun()

                    except Exception as exc:

                        st.error(
                            f"Could not start session: {exc}"
                        )

            elif status == "in_progress":

                if st.button(
                    f"✅ Complete Session {session_number}",
                    key=f"complete_session_{session_number}",
                ):

                    try:

                        finish_study_session(
                            plan,
                            session_number,
                        )

                        st.session_state[
                            "study_plan"
                        ] = plan

                        st.rerun()

                    except Exception as exc:

                        st.error(
                            f"Could not complete session: {exc}"
                        )

            else:

                st.caption(
                    "This session is completed."
                )

        spacer(12)

    # =========================================================
    # ALL SESSIONS COMPLETED
    # =========================================================

    if completed_count == len(sessions):

        st.success(
            "🎉 Congratulations! "
            "You have completed your entire study plan."
        )