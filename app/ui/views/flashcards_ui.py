"""Flashcards view — 3D CSS flip cards with SM-2 spaced repetition."""

import streamlit as st

from app.ui.backend import get_flashcards, submit_flashcard_answer
from app.ui.components import hero, render_flashcard, spacer


def render_flashcard_ui():
    hero(
        eyebrow="Spaced repetition",
        title="Master any topic with",
        highlight="flashcards.",
        subtitle=(
            "Generate AI-powered flashcards and review them with "
            "spaced repetition. Hover over a card to reveal the answer."
        ),
    )
    spacer(20)

    # ---------------------------------------------------------
    # 1. Initialize Session State
    # ---------------------------------------------------------
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = []
    if "current_card_idx" not in st.session_state:
        st.session_state.current_card_idx = 0

    # ---------------------------------------------------------
    # 2. Generation Controls
    # ---------------------------------------------------------
    with st.expander(
        "🛠️ Generate New Flashcards",
        expanded=not bool(st.session_state.flashcards),
    ):
        with st.form("generate_form"):
            topic = st.text_input("Topic", value="Machine Learning basics")
            count = st.number_input(
                "Number of Cards", min_value=1, max_value=20, value=5
            )
            submit_generate = st.form_submit_button(
                "Generate Cards", type="primary"
            )

        if submit_generate:
            with st.spinner("Generating high-quality flashcards..."):
                st.session_state.flashcards = get_flashcards(topic, count)
                st.session_state.current_card_idx = 0
                st.rerun()

    # ---------------------------------------------------------
    # 3. Interactive 3D Flip Card Display
    # ---------------------------------------------------------
    if st.session_state.flashcards:
        idx = st.session_state.current_card_idx
        total_cards = len(st.session_state.flashcards)

        if idx < total_cards:
            card = st.session_state.flashcards[idx]

            spacer(12)

            # Render the 3D flip card (pure CSS, no re-run for flip)
            render_flashcard(
                front=card.get("front", "Question"),
                back=card.get("back", "Answer"),
                index=idx,
                total=total_cards,
            )

            spacer(16)

            # SM-2 Rating
            st.markdown(
                "<p style='text-align:center;color:var(--muted);font-size:.88rem;'>"
                "How well did you know this?</p>",
                unsafe_allow_html=True,
            )

            cols = st.columns(6)
            ratings = [
                (0, "😵", "Blackout"),
                (1, "😰", "Barely"),
                (2, "😐", "Hard"),
                (3, "🙂", "OK"),
                (4, "😊", "Good"),
                (5, "🤩", "Perfect"),
            ]

            for col, (score, emoji, label) in zip(cols, ratings):
                with col:
                    if st.button(
                        f"{emoji} {score}",
                        key=f"rate_{idx}_{score}",
                        help=label,
                        use_container_width=True,
                    ):
                        result = submit_flashcard_answer(quality=score)
                        next_days = result.get("next_interval_days", 1)
                        st.toast(
                            f"Recorded! Next review in {next_days} days.",
                            icon="✅",
                        )
                        st.session_state.current_card_idx += 1
                        st.rerun()

        else:
            spacer(24)
            st.markdown(
                """
                <div class="welcome-banner" style="padding:32px;">
                  <div class="wb-emoji">🎉</div>
                  <h2>All cards reviewed!</h2>
                  <p class="wb-sub">
                    Great work! Generate more cards or revisit this set.
                  </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            spacer(12)
            if st.button("🔄 Start Over", type="primary"):
                st.session_state.flashcards = []
                st.session_state.current_card_idx = 0
                st.rerun()
