"""Mind Map view — generate mind maps from topics or study material."""

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
            help="What should the mind map be about?"
        )
        
        submitted = st.form_submit_button("Generate Mind Map", type="primary")

    if submitted:
        if not topic.strip():
            st.warning("Please enter a topic.")
            return

        with st.spinner("🧠 Agent generating mind map..."):
            mindmap_code = generate_mindmap(
                topic=topic,
                document_id=document
            )

        if not mindmap_code:
            st.error("Failed to generate mind map. Please try again.")
            return

        st.subheader(f"Interactive Mind Map: {topic}")
        st.markdown(f"```mermaid\n{mindmap_code}\n```")
        
        with st.expander("Show Mermaid Source Code"):
            st.code(mindmap_code, language="mermaid")
