"""Sidebar: study materials, chat history, settings."""

import streamlit as st

from app.ui.backend import ingest_document
from app.ui.utils import create_new_chat, delete_chat, sync_uploads
from app.ui.styles import THEMES

AVATAR_OPTIONS_USER = ["🧑‍🎓", "🧑‍💻", "👩‍🎓", "👨‍🎓", "🦉", "🐱", "🤓", "🧑"]
AVATAR_OPTIONS_TUTOR = ["🎓", "🤖", "🧠", "📚", "✨", "🦾", "🦊", "🐣"]


def render_sidebar():
    with st.sidebar:
        st.markdown(
            "<h1 style='margin-bottom:0'>🎓 AI Tutor</h1>"
            "<p style='color:var(--muted);font-size:.85rem;margin:.2rem 0 0'>"
            "Multi-agent RAG learning assistant</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        # ============================================================
        # STUDY MATERIALS
        # ============================================================

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
            for f in files:
                if f.name not in already:
                    ingest_document(f)
                    already.add(f.name)
            st.session_state.ingested_files = already
            st.caption(
                f"✅ {len(files)} document{'s' if len(files) != 1 else ''} indexed for retrieval."
            )
        else:
            st.caption("No material yet — answers will use web fallback.")

        st.divider()

        # ============================================================
        # NEW CHAT
        # ============================================================

        if st.button("➕ New Chat", type="primary", key="new_chat_btn"):
            create_new_chat()
            st.rerun()

        # ============================================================
        # CHAT HISTORY
        # ============================================================

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
                        st.rerun()
                with col_del:
                    if st.button("✕", key=f"del_{chat_id}", help="Delete chat"):
                        delete_chat(chat_id)
                        st.rerun()

        st.divider()

        # ============================================================
        # QUICK OPTIONS
        # ============================================================

        with st.expander("🔧 Quick Options", expanded=False):
            st.session_state.show_sources = st.checkbox(
                "Show sources", value=st.session_state.show_sources
            )
            st.session_state.show_confidence = st.checkbox(
                "Show confidence score", value=st.session_state.show_confidence
            )
            st.session_state.show_trace = st.checkbox(
                "Show agent pipeline trace", value=st.session_state.show_trace
            )

        # ============================================================
        # SETTINGS (moved from settings.py)
        # ============================================================

        with st.expander("⚙️ Settings", expanded=False):

            # Theme
            st.markdown("**🎨 Theme**")
            theme_names = list(THEMES.keys())
            current_theme = st.session_state.get("theme", "Midnight Aurora")
            new_theme = st.selectbox(
                "Theme",
                theme_names,
                index=theme_names.index(current_theme) if current_theme in theme_names else 0,
                label_visibility="collapsed",
            )
            if new_theme != current_theme:
                st.session_state.theme = new_theme
                st.rerun()

            # Font size
            new_font = st.select_slider(
                "Font size",
                options=["Small", "Medium", "Large"],
                value=st.session_state.font_size,
            )
            if new_font != st.session_state.font_size:
                st.session_state.font_size = new_font
                st.rerun()

            # Chat density
            new_density = st.select_slider(
                "Chat density",
                options=["Compact", "Comfortable"],
                value=st.session_state.chat_density,
            )
            if new_density != st.session_state.chat_density:
                st.session_state.chat_density = new_density
                st.rerun()

            # Animations
            new_anim = st.toggle(
                "Enable animations",
                value=st.session_state.animations_enabled,
            )
            if new_anim != st.session_state.animations_enabled:
                st.session_state.animations_enabled = new_anim
                st.rerun()

            # Avatars
            st.markdown("**🧑‍🎓 Avatars**")
            idx_u = (
                AVATAR_OPTIONS_USER.index(st.session_state.user_avatar)
                if st.session_state.user_avatar in AVATAR_OPTIONS_USER
                else 0
            )
            new_user_avatar = st.selectbox("Your avatar", AVATAR_OPTIONS_USER, index=idx_u)
            if new_user_avatar != st.session_state.user_avatar:
                st.session_state.user_avatar = new_user_avatar
                st.rerun()

            idx_t = (
                AVATAR_OPTIONS_TUTOR.index(st.session_state.assistant_avatar)
                if st.session_state.assistant_avatar in AVATAR_OPTIONS_TUTOR
                else 0
            )
            new_tutor_avatar = st.selectbox("Tutor avatar", AVATAR_OPTIONS_TUTOR, index=idx_t)
            if new_tutor_avatar != st.session_state.assistant_avatar:
                st.session_state.assistant_avatar = new_tutor_avatar
                st.rerun()

    return files