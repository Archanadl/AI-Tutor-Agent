"""AI Tutor Agent — Streamlit frontend (Member 5)."""

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
from app.ui.views import chat, flashcards_ui, home, progress, quiz, settings, study_plan, mindmap

page_config()
init_state()      # must run before inject_theme(), which reads saved preferences

render_sidebar()

ROUTES = {
    "Home": home.render,
    "Chat": chat.render,
    "Quiz": quiz.render,
    "Flashcards": flashcards_ui.render_flashcard_ui,
    "Mind Map": mindmap.render,
    "Study Plan": study_plan.render,
    "Progress": progress.render,
    "Settings": settings.render,
}

ROUTES.get(st.session_state.page, home.render)()