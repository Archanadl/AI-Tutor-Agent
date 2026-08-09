"""AI Tutor Agent — Streamlit frontend (Member 5)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st                        # noqa: E402

from sidebar import render_sidebar            # noqa: E402
from styles import inject_theme, page_config   # noqa: E402
from utils import init_state                   # noqa: E402
from views import chat, home, progress, quiz, settings, study_plan  # noqa: E402

page_config()
init_state()      # must run before inject_theme(), which reads saved preferences
inject_theme()

render_sidebar()

ROUTES = {
    "Home": home.render,
    "Chat": chat.render,
    "Quiz": quiz.render,
    "Study Plan": study_plan.render,
    "Progress": progress.render,
    "Settings": settings.render,
}

ROUTES.get(st.session_state.page, home.render)()