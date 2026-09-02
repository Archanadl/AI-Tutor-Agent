"""AI Tutor Agent — Streamlit frontend with modern tab-based layout."""

import os
import sys

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from app.ui.sidebar import render_sidebar
from app.ui.styles import inject_theme, page_config
from app.ui.utils import init_state
from app.ui.views import chat, flashcards_ui, quiz, study_plan, mindmap

page_config()
init_state()

# Inject theme CSS (reads saved preferences from session state)
inject_theme()

# Render the simplified sidebar (PDF upload, chat history, settings)
render_sidebar()

# ============================================================
# TAB-BASED NAVIGATION
# ============================================================

tab_tutor, tab_plan, tab_learn, tab_mind = st.tabs([
    "💬 AI Tutor",
    "📅 Study Plan & Progress",
    "🃏 Flashcards & Quizzes",
    "🧠 Mindmap",
])

with tab_tutor:
    chat.render()

with tab_plan:
    study_plan.render()

with tab_learn:
    # Sub-tabs for Flashcards and Quizzes
    fc_tab, quiz_tab = st.tabs(["📇 Flashcards", "📝 Quizzes"])
    with fc_tab:
        flashcards_ui.render_flashcard_ui()
    with quiz_tab:
        quiz.render()

with tab_mind:
    mindmap.render()