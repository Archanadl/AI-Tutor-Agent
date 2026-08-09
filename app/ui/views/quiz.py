"""Quiz view — generation settings, attempt flow, scoring + feedback."""

import streamlit as st

from backend import generate_quiz
from components import hero, spacer, stat


def render():
    hero(
        eyebrow="Assessment agent",
        title="Turn your notes into a",
        highlight="quiz.",
        subtitle="Pick a topic and difficulty; the quiz agent builds questions from your material.",
    )
    spacer(24)

    col1, col2 = st.columns(2)
    with col1:
        topic = st.selectbox(
            "📚 Topic",
            [
                "Entire Document",
                "Computer Networks",
                "Database Management Systems",
                "Operating Systems",
                "Machine Learning",
            ],
        )
    with col2:
        difficulty = st.select_slider("🎯 Difficulty", ["Easy", "Medium", "Hard"], value="Medium")

    count = st.slider("Number of questions", 3, 15, 5)

    spacer(8)
    if st.button("🚀 Generate quiz", type="primary", key="gen_quiz"):
        st.session_state.quiz_started = True
        st.session_state.quiz_score = None
        st.session_state.quiz_items = generate_quiz(topic, difficulty, count)
        st.rerun()

    if not st.session_state.quiz_started:
        return

    items = st.session_state.get("quiz_items", [])
    spacer(18)
    st.subheader(f"📝 {topic}")
    st.caption(f"{difficulty} · {len(items)} questions")

    answers = []
    for i, item in enumerate(items):
        with st.container(border=True):
            st.markdown(f"**{i + 1}. {item['q']}**")
            answers.append(
                st.radio("Select one", item["options"], key=f"quiz_{i}", label_visibility="collapsed")
            )

    spacer(10)
    if st.button("✅ Submit quiz", type="primary", key="submit_quiz"):
        score = sum(1 for a, item in zip(answers, items) if a == item["answer"])
        st.session_state.quiz_score = (score, len(items))
        st.rerun()

    if st.session_state.quiz_score:
        score, total = st.session_state.quiz_score
        pct = round(score / total * 100)
        spacer(14)
        a, b, c = st.columns(3)
        with a:
            stat("Score", f"{score}/{total}", "", 1)
        with b:
            stat("Percentage", f"{pct}%", "", 2)
        with c:
            stat("Verdict", "Strong" if pct >= 70 else "Needs revision", "", 3)

        st.progress(pct / 100)
        spacer(10)
        st.subheader("🧾 Review")
        for i, item in enumerate(items):
            picked = st.session_state.get(f"quiz_{i}")
            ok = picked == item["answer"]
            with st.expander(f"{'✅' if ok else '❌'} {i + 1}. {item['q']}"):
                st.write(f"**Your answer:** {picked}")
                st.write(f"**Correct answer:** {item['answer']}")
                st.caption(item["why"])
