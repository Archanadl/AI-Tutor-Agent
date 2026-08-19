"""Progress view — activity metrics, topic mastery, weak areas."""

import streamlit as st

from components import hero, spacer, stat

TOPIC_SCORES = {
    "Computer Networks": 82,
    "Database Management Systems": 74,
    "Operating Systems": 61,
    "Machine Learning": 88,
}


def render():
    hero(
        eyebrow="Analytics",
        title="See what's solid and what still",
        highlight="needs work.",
        subtitle="Mastery is derived from quiz scores, revisits and the topics you ask about most.",
    )
    spacer(24)

    cols = st.columns(4)
    metrics = [
        ("Topics studied", "8", "+2 this week"),
        ("Quizzes taken", "4", "avg 78%"),
        ("Average score", "78%", "+6% trend"),
        ("Study streak", "3 days", "keep going 🔥"),
    ]
    for i, (col, m) in enumerate(zip(cols, metrics), start=1):
        with col:
            stat(m[0], m[1], m[2], delay=i)

    spacer(30)
    st.subheader("📚 Topic mastery")
    for topic, score in TOPIC_SCORES.items():
        label = "Strong" if score >= 80 else "Fair" if score >= 70 else "Weak"
        st.markdown(
            f"<div style='display:flex;justify-content:space-between'>"
            f"<b>{topic}</b><span style='color:var(--muted)'>{label} · {score}%</span></div>",
            unsafe_allow_html=True,
        )
        st.progress(score / 100)
        spacer(6)

    spacer(20)
    st.subheader("🧠 Weak topics")
    a, b = st.columns(2)
    with a:
        st.warning("Operating System Scheduling — 61%")
    with b:
        st.warning("DBMS Normalization — 74%")

    spacer(20)
    st.subheader("🔄 Revision recommendations")
    st.info("Spend 30 minutes on OS scheduling, then retake the quiz to confirm.")
    st.info("Re-read the normalization section and attempt 5 practice questions.")
