"""Home / dashboard view."""

import streamlit as st

from components import card, hero, spacer, stat
from utils import create_new_chat, goto


def render():
    hero(
        eyebrow="Multi-agent · RAG · LangGraph",
        title="Study with a tutor that actually",
        highlight="reads your material.",
        subtitle=(
            "Upload your notes and textbooks, then ask anything. Every answer shows "
            "where it came from, how confident the tutor is, and which agents ran."
        ),
    )
    spacer(26)

    materials = len(st.session_state.uploaded_files)
    cols = st.columns(4)
    stats = [
        ("Materials", str(materials), "Indexed for retrieval" if materials else "Upload a PDF"),
        ("Conversations", str(len(st.session_state.chats)), "Session memory on"),
        ("Quizzes", "0" if st.session_state.quiz_score is None else "1", "Auto-generated"),
        ("Study streak", "3 days", "Keep it going 🔥"),
    ]
    for i, (col, item) in enumerate(zip(cols, stats), start=1):
        with col:
            stat(item[0], item[1], item[2], delay=i)

    spacer(30)
    st.subheader("🚀 How it works")
    cols = st.columns(3)
    steps = [
        ("📚", "1 · Upload", "Your PDFs are parsed, chunked and embedded into a vector store."),
        ("🧠", "2 · Ask", "Retrieval runs, a grader agent checks relevance, web search backs it up."),
        ("🎯", "3 · Verify", "Answers arrive with a source badge and a confidence score."),
    ]
    for i, (col, step) in enumerate(zip(cols, steps), start=1):
        with col:
            card(step[0], step[1], step[2], delay=i)

    spacer(30)
    st.subheader("⚡ Quick actions")
    a, b, c = st.columns(3)
    with a:
        if st.button("💬 Start learning", type="primary", key="qa_chat"):
            create_new_chat()
            st.rerun()
    with b:
        if st.button("📝 Generate a quiz", key="qa_quiz"):
            goto("Quiz")
            st.rerun()
    with c:
        if st.button("📅 View study plan", key="qa_plan"):
            goto("Study Plan")
            st.rerun()

    spacer(30)
    st.subheader("🔄 Recommended revision")
    for i, topic in enumerate(
        ["TCP three-way handshake", "DBMS normalization", "SQL joins practice"]
    ):
        st.checkbox(topic, key=f"rev_{i}")
