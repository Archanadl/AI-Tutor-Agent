"""Study plan & progress view — unified dashboard with timeline and metrics."""

from datetime import date, timedelta

import streamlit as st

from app.ui.components import hero, metric_card, spacer, timeline_item

from app.ui.backend import (
    create_study_plan,
    begin_study_session,
    finish_study_session,
)

from app.progress import (
    record_study_session,
    get_progress_summary,
    get_topic_mastery,
    get_weak_topics,
    get_study_streak,
    get_recommendations,
)


def render():
    hero(
        eyebrow="Plan & track",
        title="Your personalized study",
        highlight="dashboard.",
        subtitle=(
            "Create study plans, track your progress, and identify "
            "weak areas — all in one place."
        ),
    )

    spacer(20)

    # =========================================================
    # SUB-TABS: Study Plan / Progress
    # =========================================================

    plan_tab, progress_tab = st.tabs(["📅 Study Plan", "📈 Progress"])

    with plan_tab:
        _render_study_plan()

    with progress_tab:
        _render_progress()


# ============================================================
# STUDY PLAN
# ============================================================

def _render_study_plan():
    spacer(12)

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

    exam_date = None
    if plan_type == "Exam Preparation":
        exam_date = st.date_input(
            "📅 Exam date",
            value=date.today() + timedelta(days=7),
        )

    st.caption(
        "Your plan contains study sessions, not fixed calendar days. "
        "You can complete sessions consecutively or whenever you have time."
    )

    generate_plan = st.button(
        "✨ Generate Personalized Study Plan",
        type="primary",
    )

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

                if "error" in plan:
                    st.error(
                        f"Could not generate study plan: {plan['error']}"
                    )
                elif not plan.get("study_sessions"):
                    st.error("The planner returned no study sessions.")
                else:
                    st.session_state["study_plan"] = plan
                    st.success("✅ Personalized study plan generated successfully!")

            except Exception as exc:
                st.error(f"Could not generate study plan: {exc}")

    # =========================================================
    # DISPLAY GENERATED STUDY PLAN
    # =========================================================

    plan = st.session_state.get("study_plan")
    if not plan:
        return

    sessions = plan.get("study_sessions", [])
    if not sessions:
        st.warning("No study sessions were generated.")
        return

    spacer(28)
    st.subheader("📖 Your Study Plan")

    # Progress summary cards
    completed_count = sum(
        1 for session in sessions
        if session.get("status") == "completed"
    )
    remaining_count = len(sessions) - completed_count
    progress = completed_count / len(sessions)

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("📚", "Total Sessions", str(len(sessions)), "Study sessions planned")
    with col2:
        metric_card("✅", "Completed", str(completed_count), f"{round(progress * 100)}% done")
    with col3:
        metric_card("📋", "Remaining", str(remaining_count), "Sessions left")

    spacer(12)
    st.progress(progress, text=f"{completed_count} of {len(sessions)} sessions completed")

    spacer(20)

    # =========================================================
    # TIMELINE VIEW
    # =========================================================

    st.markdown('<div class="timeline">', unsafe_allow_html=True)

    for session in sessions:
        session_number = session.get("session")
        status = session.get("status", "pending")
        tasks = session.get("tasks", [])
        total_minutes = sum(
            task.get("duration_minutes", 0) for task in tasks
        )

        # Render the timeline card (HTML)
        timeline_item(
            number=session_number,
            status=status,
            tasks=tasks,
            total_minutes=total_minutes,
        )

        # Action buttons (Streamlit native, placed after the HTML card)
        if status == "pending":
            if st.button(
                f"▶️ Start Session {session_number}",
                key=f"start_session_{session_number}",
            ):
                try:
                    begin_study_session(plan, session_number)
                    st.session_state["study_plan"] = plan
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not start session: {exc}")

        elif status == "in_progress":
            if st.button(
                f"✅ Complete Session {session_number}",
                key=f"complete_session_{session_number}",
                type="primary",
            ):
                try:
                    finish_study_session(plan, session_number)
                    record_study_session(
                        session_number=session_number,
                        topics=[
                            task.get("topic", "Study topic")
                            for task in tasks
                        ],
                        duration_minutes=total_minutes,
                    )
                    st.session_state["study_plan"] = plan
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not complete session: {exc}")

    st.markdown('</div>', unsafe_allow_html=True)

    # All completed banner
    if completed_count == len(sessions):
        spacer(12)
        st.markdown(
            """
            <div class="welcome-banner" style="padding:28px;">
              <div class="wb-emoji">🎉</div>
              <h2>Congratulations!</h2>
              <p class="wb-sub">You have completed your entire study plan.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# PROGRESS TRACKER
# ============================================================

def _render_progress():
    spacer(12)

    progress_summary = get_progress_summary()
    topic_mastery = get_topic_mastery()
    weak_topics = get_weak_topics()
    study_streak = get_study_streak()
    recommendations = get_recommendations()

    # Dashboard metric cards
    cols = st.columns(4)
    metrics = [
        ("📚", "Topics Studied", str(progress_summary.get("topics_studied", 0)), "From your learning activity"),
        ("📝", "Quizzes Taken", str(progress_summary.get("quizzes_taken", 0)), "Completed attempts"),
        ("🎯", "Average Score", f"{progress_summary.get('average_score', 0)}%", "Across completed quizzes"),
        ("🔥", "Study Streak", f"{study_streak} days", "Keep going!"),
    ]

    for col, m in zip(cols, metrics):
        with col:
            metric_card(m[0], m[1], m[2], m[3])

    spacer(30)

    # Topic mastery
    st.subheader("📚 Topic Mastery")

    if topic_mastery:
        for topic_name, data in topic_mastery.items():
            score = data.get("mastery", 0)
            level = data.get("level", "Weak")

            st.markdown(
                f"<div style='display:flex;justify-content:space-between;margin-bottom:4px;'>"
                f"<b>{topic_name}</b>"
                f"<span style='color:var(--muted)'>{level} · {score}%</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.progress(score / 100)
            spacer(6)
    else:
        st.info("📚 Topic mastery will appear after you complete quizzes.")

    spacer(20)

    # Weak topics
    st.subheader("🧠 Weak Topics")

    if weak_topics:
        cols = st.columns(min(len(weak_topics), 3))
        for i, item in enumerate(weak_topics):
            with cols[i % len(cols)]:
                st.warning(f"📌 {item['topic']} — {item['mastery']}%")
    else:
        st.success("🎉 No weak topics detected yet. Keep practicing!")

    spacer(20)

    # Recommendations
    st.subheader("🔄 Revision Recommendations")

    if recommendations:
        for recommendation in recommendations:
            st.info(f"💡 {recommendation['message']}")
    else:
        st.success(
            "🎯 Keep practicing! Recommendations will appear as you "
            "complete quizzes and study sessions."
        )