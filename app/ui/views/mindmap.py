"""Mind Map view — generate interactive mind maps from topics or study material."""

import streamlit as st

from app.ui.backend import generate_mindmap
from app.ui.components import hero, spacer
from app.ui.utils import primary_document


def render():
    hero(
        eyebrow="Visualize",
        title="Mind",
        highlight="Maps",
        subtitle="Generate interactive concept maps from your study material or custom topics.",
    )
    spacer(20)

    document = primary_document()
    default_topic = "Document Summary" if document else ""

    with st.form("mindmap_form"):
        topic = st.text_input(
            "Topic or Concept",
            value=default_topic,
            help="What should the mind map be about?",
        )

        submitted = st.form_submit_button("Generate Mind Map", type="primary")

    if submitted:
        if not topic.strip():
            st.warning("Please enter a topic.")
            return

        with st.spinner("🧠 Agent generating mind map..."):
            mindmap_code = generate_mindmap(
                topic=topic,
                document_id=document,
            )

        if not mindmap_code:
            st.error("Failed to generate mind map. Please try again.")
            return

        st.session_state["last_mindmap"] = {
            "topic": topic,
            "code": mindmap_code,
        }
        st.rerun()

    # Display the last generated mindmap
    mindmap_data = st.session_state.get("last_mindmap")
    if mindmap_data:
        spacer(12)

        # Styled header
        st.markdown(
            f"""
            <div style="
                border: 1px solid var(--border);
                border-radius: 20px 20px 0 0;
                padding: 18px 24px;
                background: linear-gradient(
                    135deg,
                    color-mix(in srgb, var(--primary) 8%, var(--surface)),
                    var(--surface)
                );
            ">
              <div style="font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:4px;">Mind Map</div>
              <div style="font-family:'Sora',sans-serif;font-size:1.2rem;font-weight:600;">🗺️ {mindmap_data['topic']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Mermaid rendering (Streamlit handles this natively)
        st.markdown(f"```mermaid\n{mindmap_data['code']}\n```")

        spacer(12)
        with st.expander("📄 Show Mermaid Source Code"):
            st.code(mindmap_data["code"], language="mermaid")
