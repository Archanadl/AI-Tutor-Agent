import streamlit as st
from app.ui.backend import get_flashcards, submit_flashcard_answer

def render_flashcard_ui():
    st.header("📇 Flashcard Practice")
    st.write("Generate custom flashcards and study them using spaced repetition.")

    # ---------------------------------------------------------
    # 1. Initialize Session State
    # ---------------------------------------------------------
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = []
    if "current_card_idx" not in st.session_state:
        st.session_state.current_card_idx = 0
    if "is_flipped" not in st.session_state:
        st.session_state.is_flipped = False

    # ---------------------------------------------------------
    # 2. Generation Controls
    # ---------------------------------------------------------
    with st.expander("🛠️ Generate New Flashcards", expanded=not bool(st.session_state.flashcards)):
        with st.form("generate_form"):
            # Defaulting to Machine Learning to match your current academic focus
            topic = st.text_input("Topic", value="Machine Learning basics")
            count = st.number_input("Number of Cards", min_value=1, max_value=20, value=5)
            submit_generate = st.form_submit_button("Generate Cards")

        if submit_generate:
            with st.spinner("Generating high-quality flashcards..."):
                st.session_state.flashcards = get_flashcards(topic, count)
                st.session_state.current_card_idx = 0
                st.session_state.is_flipped = False
                st.rerun()

    # ---------------------------------------------------------
    # 3. Interactive Card Display
    # ---------------------------------------------------------
    if st.session_state.flashcards:
        idx = st.session_state.current_card_idx
        total_cards = len(st.session_state.flashcards)

        if idx < total_cards:
            card = st.session_state.flashcards[idx]
            
            st.markdown("---")
            st.subheader(f"Card {idx + 1} of {total_cards}")
            
            # The Card Container
            card_container = st.container()
            
            # SHOW FRONT
            card_container.info(f"**Question:**\n\n### {card.get('front')}")
            
            # SHOW BACK (If flipped)
            if not st.session_state.is_flipped:
                if st.button("🔄 Flip Card", use_container_width=True):
                    st.session_state.is_flipped = True
                    st.rerun()
            else:
                card_container.success(f"**Answer:**\n\n### {card.get('back')}")
                
                st.markdown("#### How well did you know this?")
                
                # Rating Buttons (0-5)
                cols = st.columns(6)
                ratings = [
                    (0, "0 - Complete Blackout"), 
                    (1, "1 - Barely Remembered"), 
                    (2, "2 - Hard to Recall"), 
                    (3, "3 - OK"), 
                    (4, "4 - Good"), 
                    (5, "5 - Perfect")
                ]
                
                for col, (score, label) in zip(cols, ratings):
                    if col.button(str(score), help=label, use_container_width=True):
                        # Calculate SM-2 for the next review
                        result = submit_flashcard_answer(quality=score)
                        next_days = result.get('next_interval_days', 1)
                        st.toast(f"Recorded! Next review in {next_days} days.", icon="✅")
                        
                        # Move to the next card
                        st.session_state.current_card_idx += 1
                        st.session_state.is_flipped = False
                        st.rerun()
        else:
            st.markdown("---")
            st.success("🎉 You've completed all the flashcards in this set!")
            if st.button("Start Over / Reset"):
                st.session_state.flashcards = []
                st.session_state.current_card_idx = 0
                st.session_state.is_flipped = False
                st.rerun()