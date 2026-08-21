"""Sidebar: study materials, navigation, chat history, options."""

import streamlit as st

from app.ui.backend import ingest_document
from app.ui.utils import create_new_chat, delete_chat, goto, sync_uploads

NAV = [
    ("Home", "🏠 Home"),
    ("Chat", "💬 Chat"),
    ("Quiz", "📝 Quiz"),
    ("Flashcards", "📇 Flashcards"),
    ("Study Plan", "📅 Study Plan"),
    ("Progress", "📊 Progress"),
]


def render_sidebar():
    with st.sidebar:
        st.markdown(
            "<h1 style='margin-bottom:0'>🎓 AI Tutor</h1>"
            "<p style='color:var(--muted);font-size:.85rem;margin:.2rem 0 0'>"
            "Multi-agent RAG learning assistant</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        st.subheader("📚 Study Materials")
        files = st.file_uploader(
            "Drop your PDFs here",
            type=["pdf"],
            accept_multiple_files=True,
            help="Textbooks, lecture notes, syllabus or previous papers.",
            label_visibility="collapsed",
        )
        sync_uploads(files)
        if files:
            already = st.session_state.get("ingested_files", set())
            newly_ingested = 0
            for f in files:
                if f.name not in already:
                    ingest_document(f)
                    already.add(f.name)
                    newly_ingested += 1
            st.session_state.ingested_files = already
            st.caption(
                f"✅ {len(files)} document{'s' if len(files) != 1 else ''} indexed for retrieval."
            )
        else:
            st.caption("No material yet — answers will use web fallback.")

        st.divider()

        if st.button("➕ New Chat", type="primary", key="new_chat_btn"):
            create_new_chat()
            st.rerun()

        st.subheader("🧭 Learning")
        for key, label in NAV:
            active = st.session_state.page == key
            if st.button(("▸ " if active else "") + label, key=f"nav_{key}"):
                if key == "Chat" and st.session_state.current_chat is None:
                    create_new_chat()
                else:
                    goto(key)
                st.rerun()

        st.divider()

        st.subheader("💬 Chat History")
        if not st.session_state.chats:
            st.caption("No conversations yet.")
        else:
            for chat_id, chat in list(st.session_state.chats.items())[::-1]:
                col_open, col_del = st.columns([5, 1])
                marker = "🟢" if chat_id == st.session_state.current_chat else "📌"
                with col_open:
                    if st.button(f"{marker} {chat['title']}", key=f"hist_{chat_id}"):
                        st.session_state.current_chat = chat_id
                        goto("Chat")
                        st.rerun()
                with col_del:
                    if st.button("✕", key=f"del_{chat_id}", help="Delete chat"):
                        delete_chat(chat_id)
                        st.rerun()

        st.divider()

        with st.expander("⚙️ Quick Options", expanded=False):
            st.session_state.show_sources = st.checkbox(
                "Show sources", value=st.session_state.show_sources
            )
            st.session_state.show_confidence = st.checkbox(
                "Show confidence score", value=st.session_state.show_confidence
            )
            st.session_state.show_trace = st.checkbox(
                "Show agent pipeline trace", value=st.session_state.show_trace
            )
            st.caption("For theme, fonts and avatars, open the ⚙️ Settings page.")
    return files