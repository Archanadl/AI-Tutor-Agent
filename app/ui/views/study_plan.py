"""Study plan view — exam date, daily hours, generated schedule."""

from datetime import date, timedelta

import streamlit as st

from components import card, hero, spacer, stat


def render():
    hero(
        eyebrow="Planner agent",
        title="A schedule shaped around your",
        highlight="exam date.",
        subtitle="Tell the planner when you're writing and how long you can study each day.",
    )
    spacer(24)

    col1, col2 = st.columns(2)
    with col1:
        exam_date = st.date_input("📅 Exam date", value=date.today() + timedelta(days=14))
    with col2:
        hours = st.slider("⏱️ Daily study time (hours)", 1, 8, 3)

    days_left = max((exam_date - date.today()).days, 0)
    spacer(16)
    a, b, c = st.columns(3)
    with a:
        stat("Days left", str(days_left), "until the exam", 1)
    with b:
        stat("Total hours", str(days_left * hours), "planned capacity", 2)
    with c:
        stat("Sessions/day", str(max(hours * 2, 2)), "25-min blocks", 3)

    spacer(28)
    st.subheader("📖 Today's plan")
    tasks = [
        ("Revise TCP three-way handshake", "30 min", "🔁 Weak topic"),
        ("Study sliding window protocol", "45 min", "🆕 New"),
        ("Take a Computer Networks quiz", "30 min", "📝 Practice"),
        ("Review flagged flashcards", "20 min", "🧠 Recall"),
    ]
    for i, (task, duration, tag) in enumerate(tasks):
        with st.container(border=True):
            left, right = st.columns([6, 2])
            with left:
                st.checkbox(f"**{task}**", key=f"task_{i}")
            with right:
                st.caption(f"{tag} · {duration}")

    spacer(26)
    st.subheader("🗓️ Week ahead")
    cols = st.columns(3)
    plan = [
        ("📡", "Networks", "TCP, UDP, congestion control, sliding window."),
        ("🗄️", "DBMS", "Normalization up to BCNF, joins, transactions."),
        ("🖥️", "Operating Systems", "Scheduling, deadlocks, memory management."),
    ]
    for i, (col, item) in enumerate(zip(cols, plan), start=1):
        with col:
            card(item[0], item[1], item[2], delay=i)

    spacer(20)
    st.info("Based on your quiz history, prioritise OS scheduling and DBMS normalization.")
