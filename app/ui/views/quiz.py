"""Quiz view — generation settings, styled option cards, scoring + feedback."""

import streamlit as st

from app.ui.backend import generate_quiz
from app.ui.components import hero, metric_card, spacer
from app.progress import record_quiz_attempt


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
        topic = st.text_input(
            "📚 Topic",
            value="Computer Networks",
            placeholder="Type any topic here...",
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
        st.session_state.quiz_submitted = False

        # Clear previous answers
        for key in list(st.session_state.keys()):
            if key.startswith("quiz_sel_"):
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

    items = st.session_state.get("quiz_items", [])

    if not items:
        st.warning("No quiz questions are available.")
        return

    spacer(18)

    st.subheader(f"📝 {topic}")
    st.caption(f"{difficulty} · {len(items)} questions")

    submitted = st.session_state.get("quiz_submitted", False)

    # ---------------------------------------------------------
    # QUESTIONS — Styled Option Cards
    # ---------------------------------------------------------

    for i, item in enumerate(items):
        spacer(6)

        st.markdown(f"**{i + 1}. {item['q']}**")

        current_sel = st.session_state.get(f"quiz_sel_{i}", None)
        markers = ["A", "B", "C", "D", "E", "F", "G", "H"]

        for j, option in enumerate(item["options"]):
            marker = markers[j] if j < len(markers) else str(j + 1)
            is_selected = current_sel == option
            is_correct = submitted and option == item["answer"]
            is_wrong = submitted and is_selected and option != item["answer"]

            # Determine CSS class
            css_classes = ["quiz-option"]
            if is_selected:
                css_classes.append("selected")
            if is_correct:
                css_classes.append("correct")
            if is_wrong:
                css_classes.append("wrong")

            # Determine marker content for post-submit
            if is_correct:
                marker_display = "✓"
            elif is_wrong:
                marker_display = "✗"
            else:
                marker_display = marker

            if not submitted:
                # Use a button that looks like a card
                if st.button(
                    f"{marker}. {option}",
                    key=f"qopt_{i}_{j}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary",
                ):
                    st.session_state[f"quiz_sel_{i}"] = option
                    st.rerun()
            else:
                # Post-submission: show styled result cards
                st.markdown(
                    f"""
                    <div class="{' '.join(css_classes)}">
                      <div class="qo-marker">{marker_display}</div>
                      <div>{option}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ---------------------------------------------------------
    # SUBMIT QUIZ
    # ---------------------------------------------------------

    spacer(10)

    if not submitted:
        if st.button(
            "✅ Submit quiz",
            type="primary",
            key="submit_quiz",
        ):
            answers = [
                st.session_state.get(f"quiz_sel_{i}", None)
                for i in range(len(items))
            ]

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
                    for answer, item in zip(answers, items)
                    if answer == item["answer"]
                )
                record_quiz_attempt(
                    topic=topic,
                    difficulty=difficulty,
                    score=score,
                    total=len(items),
                    questions=items,
                )
                st.session_state.quiz_score = (score, len(items))
                st.session_state.quiz_submitted = True
                st.rerun()

    # ---------------------------------------------------------
    # RESULTS
    # ---------------------------------------------------------

    if st.session_state.quiz_score is not None:

        score, total = st.session_state.quiz_score
        pct = round(score / total * 100)

        spacer(20)

        a, b, c = st.columns(3)

        with a:
            metric_card(
                "🎯",
                "Score",
                f"{score}/{total}",
                "Questions correct",
            )

        with b:
            metric_card(
                "📊",
                "Percentage",
                f"{pct}%",
                "Overall accuracy",
            )

        with c:
            metric_card(
                "🏆",
                "Verdict",
                "Strong" if pct >= 70 else "Needs revision",
                "Keep practicing!" if pct < 70 else "Well done!",
            )

        spacer(12)
        st.progress(pct / 100)

        spacer(16)

        st.subheader("🧾 Review")

        for i, item in enumerate(items):
            picked = st.session_state.get(f"quiz_sel_{i}")
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
                st.caption(item["why"])