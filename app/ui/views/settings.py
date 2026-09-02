"""Settings view — theme, typography, density, motion and avatar preferences."""

import streamlit as st

from app.ui.components import hero, spacer
from app.ui.styles import THEMES

AVATAR_OPTIONS_USER = ["🧑‍🎓", "🧑‍💻", "👩‍🎓", "👨‍🎓", "🦉", "🐱", "🤓", "🧑"]
AVATAR_OPTIONS_TUTOR = ["🎓", "🤖", "🧠", "📚", "✨", "🦾", "🦊", "🐣"]


def render():
    hero(
        eyebrow="Preferences",
        title="Make the tutor feel",
        highlight="like yours.",
        subtitle=(
            "Pick a theme, tune typography and density, and choose the avatars "
            "used across your chats. Changes apply immediately for this session."
        ),
    )
    spacer(26)

    # ---------------------------------------------------------------- theme
    st.subheader("🎨 Theme")
    theme_names = list(THEMES.keys())
    cols = st.columns(len(theme_names))
    for col, name in zip(cols, theme_names):
        swatch = THEMES[name]
        is_active = st.session_state.theme == name
        with col:
            st.markdown(
                f"""
                <div style="border-radius:14px;overflow:hidden;
                            border:1.5px solid {'var(--primary)' if is_active else 'var(--border)'};">
                  <div style="height:52px;background:linear-gradient(135deg,
                              {swatch['primary']},{swatch['primary_2']},{swatch['accent']});"></div>
                  <div style="padding:8px 10px;background:{swatch['bg_soft']};
                              color:{swatch['text']};font-size:.78rem;font-weight:600;">
                    {name}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            label = "✓ Active" if is_active else "Use theme"
            if st.button(label, key=f"theme_{name}", disabled=is_active):
                st.session_state.theme = name
                st.rerun()

    spacer(28)

    # ------------------------------------------------------ typography/layout
    st.subheader("🔤 Typography & Layout")
    c1, c2 = st.columns(2)
    with c1:
        new_font = st.select_slider(
            "Font size",
            options=["Small", "Medium", "Large"],
            value=st.session_state.font_size,
        )
        if new_font != st.session_state.font_size:
            st.session_state.font_size = new_font
            st.rerun()
    with c2:
        new_density = st.select_slider(
            "Chat density",
            options=["Compact", "Comfortable"],
            value=st.session_state.chat_density,
        )
        if new_density != st.session_state.chat_density:
            st.session_state.chat_density = new_density
            st.rerun()

    spacer(24)

    # -------------------------------------------------------------- motion
    st.subheader("✨ Motion")
    new_anim = st.toggle(
        "Enable animations",
        value=st.session_state.animations_enabled,
        help="Turn off to reduce motion across the app (fades, glows, shimmer).",
    )
    if new_anim != st.session_state.animations_enabled:
        st.session_state.animations_enabled = new_anim
        st.rerun()

    spacer(24)

    # ------------------------------------------------------------- avatars
    st.subheader("🧑‍🎓 Chat Avatars")
    c1, c2 = st.columns(2)
    with c1:
        idx = (
            AVATAR_OPTIONS_USER.index(st.session_state.user_avatar)
            if st.session_state.user_avatar in AVATAR_OPTIONS_USER
            else 0
        )
        new_user_avatar = st.selectbox("Your avatar", AVATAR_OPTIONS_USER, index=idx)
        if new_user_avatar != st.session_state.user_avatar:
            st.session_state.user_avatar = new_user_avatar
            st.rerun()
    with c2:
        idx = (
            AVATAR_OPTIONS_TUTOR.index(st.session_state.assistant_avatar)
            if st.session_state.assistant_avatar in AVATAR_OPTIONS_TUTOR
            else 0
        )
        new_tutor_avatar = st.selectbox("Tutor avatar", AVATAR_OPTIONS_TUTOR, index=idx)
        if new_tutor_avatar != st.session_state.assistant_avatar:
            st.session_state.assistant_avatar = new_tutor_avatar
            st.rerun()

    spacer(24)
    st.info(
        f"{st.session_state.user_avatar} ← that's you, "
        f"{st.session_state.assistant_avatar} ← that's your tutor, in every chat."
    )