"""Quiz view — generation settings, attempt flow, scoring + feedback."""

import streamlit as st

from backend import generate_quiz
from components import hero, spacer, stat


def render():
    hero(
        eyebrow="Assessment agent",
        title="Turn your notes into a",
        highlight="quiz.",
        subtitle=(
            "Pick a topic and difficulty; the quiz agent builds questions "
            "from your material."
        ),
    )

    spacer(24)

    # ---------------------------------------------------------
    # QUIZ SETTINGS
    # ---------------------------------------------------------

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
        difficulty = st.select_slider(
            "🎯 Difficulty",
            ["Easy", "Medium", "Hard"],
            value="Medium",
        )

    count = st.slider(
        "Number of questions",
        3,
        15,
        5,
    )

    spacer(8)

    # ---------------------------------------------------------
    # GENERATE QUIZ
    # ---------------------------------------------------------

    if st.button(
        "🚀 Generate quiz",
        type="primary",
        key="gen_quiz",
    ):
        st.session_state.quiz_started = True
        st.session_state.quiz_score = None

        # Clear previous answers and reset counters
        for key in list(st.session_state.keys()):
            if (
                key.startswith("quiz_answer_")
                or key.startswith("quiz_reset_")
            ):
                del st.session_state[key]

        # Generate fresh questions
        st.session_state.quiz_items = generate_quiz(
            topic,
            difficulty,
            count,
        )

        st.rerun()

    # ---------------------------------------------------------
    # STOP IF NO QUIZ HAS BEEN GENERATED
    # ---------------------------------------------------------

    if not st.session_state.quiz_started:
        return

    # ---------------------------------------------------------
    # GET QUIZ QUESTIONS
    # ---------------------------------------------------------

    items = st.session_state.get(
        "quiz_items",
        [],
    )

    if not items:
        st.warning("No quiz questions are available.")
        return

    spacer(18)

    st.subheader(f"📝 {topic}")
    st.caption(
        f"{difficulty} · {len(items)} questions"
    )

    # ---------------------------------------------------------
    # QUESTIONS
    # ---------------------------------------------------------

    answers = []

    for i, item in enumerate(items):

        with st.container(border=True):

            st.markdown(
                f"**{i + 1}. {item['q']}**"
            )

            # Counter used to reset the radio button
            reset_count = st.session_state.get(
                f"quiz_reset_{i}",
                0,
            )

            answer = st.radio(
                "Select one",
                item["options"],
                index=None,
                key=f"quiz_answer_{i}_{reset_count}",
                label_visibility="collapsed",
            )

            answers.append(answer)

            # -------------------------------------------------
            # CLEAR ANSWER
            # -------------------------------------------------

            if st.button(
                "↩️ Clear",
                key=f"clear_answer_{i}",
                help="Clear your selected answer",
            ):
                st.session_state[
                    f"quiz_reset_{i}"
                ] = reset_count + 1

                st.rerun()

    # ---------------------------------------------------------
    # SUBMIT QUIZ
    # ---------------------------------------------------------

    spacer(10)

    if st.button(
        "✅ Submit quiz",
        type="primary",
        key="submit_quiz",
    ):

        unanswered = [
            i + 1
            for i, answer in enumerate(answers)
            if answer is None
        ]

        if unanswered:

            st.warning(
                "⚠️ Please answer all questions before submitting."
            )

            st.info(
                "Unanswered questions: "
                + ", ".join(map(str, unanswered))
            )

        else:

            score = sum(
                1
                for answer, item in zip(
                    answers,
                    items,
                )
                if answer == item["answer"]
            )

            st.session_state.quiz_score = (
                score,
                len(items),
            )

            st.rerun()

    # ---------------------------------------------------------
    # RESULTS
    # ---------------------------------------------------------

    if st.session_state.quiz_score is not None:

        score, total = st.session_state.quiz_score

        pct = round(
            score / total * 100
        )

        spacer(14)

        a, b, c = st.columns(3)

        with a:
            stat(
                "Score",
                f"{score}/{total}",
                "",
                1,
            )

        with b:
            stat(
                "Percentage",
                f"{pct}%",
                "",
                2,
            )

        with c:
            stat(
                "Verdict",
                "Strong" if pct >= 70 else "Needs revision",
                "",
                3,
            )

        st.progress(
            pct / 100
        )

        spacer(10)

        st.subheader("🧾 Review")

        for i, item in enumerate(items):

            # Find the current answer using the current reset counter
            reset_count = st.session_state.get(
                f"quiz_reset_{i}",
                0,
            )

            picked = st.session_state.get(
                f"quiz_answer_{i}_{reset_count}"
            )

            ok = picked == item["answer"]

            with st.expander(
                f"{'✅' if ok else '❌'} "
                f"{i + 1}. {item['q']}"
            ):

                st.write(
                    f"**Your answer:** "
                    f"{picked if picked is not None else 'Not answered'}"
                )

                st.write(
                    f"**Correct answer:** "
                    f"{item['answer']}"
                )

                st.caption(
                    item["why"]
                )