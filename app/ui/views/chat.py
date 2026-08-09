"""Chat view — conversation, agent status, source grounding, confidence."""

import time

import streamlit as st

from backend import ask_tutor
from components import (
    confidence_meter,
    hero,
    skeleton,
    source_badges,
    spacer,
    trace_strip,
    typing_indicator,
)
from utils import create_new_chat, generate_chat_title, get_current_chat, primary_document

SUGGESTIONS = [
    "Explain the TCP three-way handshake",
    "Summarise this document in 10 bullet points",
    "Give me 3 exam questions on normalization",
]


def _render_meta(message: dict) -> None:
    if st.session_state.show_trace:
        trace_strip(message.get("trace"))
    if st.session_state.show_sources:
        source_badges(message.get("source"), message.get("source_type"))
    if st.session_state.show_confidence:
        confidence_meter(message.get("confidence"))


def render():
    user_avatar = st.session_state.get("user_avatar", "🧑‍🎓")
    tutor_avatar = st.session_state.get("assistant_avatar", "🎓")

    chat = get_current_chat()
    if chat is None:
        hero(
            eyebrow="Conversation",
            title="No chat open —",
            highlight="start a new one.",
            subtitle="Each conversation keeps its own memory and title.",
        )
        spacer(20)
        if st.button("➕ New chat", type="primary", key="empty_new"):
            create_new_chat()
            st.rerun()
        return

    document = primary_document()
    title = "Chat with your study material" if chat["title"] == "New Chat" else chat["title"]
    hero(
        eyebrow=f"Session · {chat['created_at']}",
        title="💬",
        highlight=title,
        subtitle=(
            f"Grounded in **{document}**" if document
            else "No document loaded — the tutor will fall back to web search."
        ),
    )
    spacer(20)

    for message in chat["messages"]:
        avatar = user_avatar if message["role"] == "user" else tutor_avatar
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                _render_meta(message)

    pending = None
    if not chat["messages"]:
        st.caption("Try one of these:")
        cols = st.columns(len(SUGGESTIONS))
        for col, text in zip(cols, SUGGESTIONS):
            with col:
                if st.button(text, key=f"sug_{text}"):
                    pending = text

    user_question = st.chat_input("Ask a question about your study material…") or pending
    if not user_question:
        return

    if not chat["messages"]:
        chat["title"] = generate_chat_title(user_question)

    chat["messages"].append({"role": "user", "content": user_question})
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(user_question)

    with st.chat_message("assistant", avatar=tutor_avatar):
        placeholder = st.container()
        with placeholder:
            typing_indicator()
            skeleton(3)

        with st.status("🤖 Agent workflow running…", expanded=True) as status:
            for line in (
                "🔍 Retrieving relevant chunks from the vector store…",
                "🧠 Grader agent evaluating context relevance…",
                "✍️ Generator agent composing the answer…",
            ):
                st.write(line)
                time.sleep(0.25)

            result = ask_tutor(
                question=user_question,
                chat_history=chat["messages"],
                document=document,
            )
            status.update(label="✅ Answer ready", state="complete", expanded=False)

        placeholder.empty()
        st.markdown(result["answer"])
        _render_meta(result)

    chat["messages"].append(
        {
            "role": "assistant",
            "content": result["answer"],
            "source": result.get("source"),
            "confidence": result.get("confidence"),
            "source_type": result.get("source_type"),
            "trace": result.get("trace", []),
        }
    )
    st.rerun()