import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Tutor",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None


# ============================================================
# CHAT TITLE GENERATOR
# ============================================================

def generate_chat_title(question):
    """
    Temporary topic-title generator.

    This will later be replaced by an LLM-based
    title generation agent.
    """

    question_lower = question.lower().strip()

    # Common topic patterns
    topic_keywords = {
        "database": "Database Management Systems",
        "dbms": "Database Management Systems",
        "normalization": "Database Normalization",
        "sql": "SQL",
        "tcp": "TCP and Networking",
        "three way handshake": "TCP Three-Way Handshake",
        "handshake": "TCP Three-Way Handshake",
        "udp": "UDP",
        "operating system": "Operating Systems",
        "os scheduling": "Operating System Scheduling",
        "scheduling": "Operating System Scheduling",
        "process": "Operating System Processes",
        "deadlock": "Operating System Deadlocks",
        "computer network": "Computer Networks",
        "network": "Computer Networks",
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning",
        "python": "Python Programming",
        "java": "Java Programming",
        "react": "React Development",
        "javascript": "JavaScript",
    }

    # Look for known topics
    for keyword, title in topic_keywords.items():

        if keyword in question_lower:
            return title

    # Fallback
    question = question.strip()

    words = question.split()

    # Remove common question words
    remove_words = {
        "what",
        "is",
        "are",
        "the",
        "a",
        "an",
        "how",
        "does",
        "do",
        "can",
        "you",
        "explain",
        "tell",
        "me",
        "about",
        "please",
        "why",
        "of",
        "in",
        "to"
    }

    useful_words = [
        word.strip("?!.,")
        for word in words
        if word.lower().strip("?!.,") not in remove_words
    ]

    useful_words = useful_words[:6]

    if not useful_words:
        return "New Chat"

    title = " ".join(useful_words)

    return title.capitalize()


# ============================================================
# CREATE NEW CHAT
# ============================================================

def create_new_chat():

    chat_number = len(st.session_state.chats) + 1

    chat_id = f"chat_{chat_number}"

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": []
    }

    st.session_state.current_chat = chat_id


# ============================================================
# GET CURRENT CHAT
# ============================================================

def get_current_chat():

    if st.session_state.current_chat is None:
        return None

    return st.session_state.chats[
        st.session_state.current_chat
    ]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # AI TUTOR HEADING
    # --------------------------------------------------------

    st.title("🎓 AI Tutor")

    st.caption(
        "Your personalized learning assistant"
    )

    st.divider()


    # ========================================================
    # STUDY MATERIALS
    # ========================================================

    st.subheader("📚 Study Materials")

    uploaded_file = st.file_uploader(
        "Upload your study material",
        type=["pdf"]
    )

    if uploaded_file:

        st.success(
            f"📄 {uploaded_file.name}"
        )


    st.divider()


    # ========================================================
    # NEW CHAT
    # ========================================================

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        create_new_chat()

        st.rerun()


    st.divider()


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    st.subheader("💬 Chat History")

    if not st.session_state.chats:

        st.caption(
            "No conversations yet."
        )

    else:

        for chat_id, chat in st.session_state.chats.items():

            title = chat["title"]

            is_current = (
                chat_id ==
                st.session_state.current_chat
            )

            if is_current:
                button_text = f"🟢 {title}"
            else:
                button_text = f"📌 {title}"

            if st.button(
                button_text,
                key=f"chat_{chat_id}",
                use_container_width=True
            ):

                st.session_state.current_chat = chat_id

                st.rerun()


    st.divider()


    # ========================================================
    # OPTIONS
    # ========================================================

    st.subheader("⚙️ Options")

    show_sources = st.checkbox(
        "Show sources",
        value=True
    )

    show_confidence = st.checkbox(
        "Show confidence score",
        value=True
    )


# ============================================================
# MAIN CONTENT
# ============================================================

if st.session_state.current_chat is None:

    st.title("🎓 Welcome to AI Tutor")

    st.subheader(
        "Start learning from your study material"
    )

    st.write(
        "Upload your PDF from the sidebar and "
        "start a new conversation."
    )

    if st.button("➕ Start New Chat"):

        create_new_chat()

        st.rerun()


else:

    current_chat = get_current_chat()


    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "💬 Chat with your study material"
    )

    if current_chat["title"] != "New Chat":

        st.caption(
            f"📌 {current_chat['title']}"
        )


    # ========================================================
    # DISPLAY CHAT MESSAGES
    # ========================================================

    for message in current_chat["messages"]:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


            # Source
            if (
                message["role"] == "assistant"
                and show_sources
                and message.get("source")
            ):

                st.caption(
                    f"📚 Source: {message['source']}"
                )


            # Confidence
            if (
                message["role"] == "assistant"
                and show_confidence
                and message.get("confidence")
            ):

                st.caption(
                    f"🎯 Confidence: "
                    f"{message['confidence']}"
                )


    # ========================================================
    # CHAT INPUT
    # ========================================================

    user_question = st.chat_input(
        "Ask a question about your study material..."
    )


    if user_question:

        # ----------------------------------------------------
        # Generate topic title
        # ----------------------------------------------------

        if len(current_chat["messages"]) == 0:

            current_chat["title"] = (
                generate_chat_title(
                    user_question
                )
            )


        # ----------------------------------------------------
        # Save user message
        # ----------------------------------------------------

        current_chat["messages"].append(
            {
                "role": "user",
                "content": user_question
            }
        )


        # ----------------------------------------------------
        # Display user message
        # ----------------------------------------------------

        with st.chat_message("user"):

            st.markdown(
                user_question
            )


        # ----------------------------------------------------
        # Temporary response
        # ----------------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "🤔 Thinking..."
            ):

                response = (
                    "This is a temporary response. "
                    "The RAG and LangGraph backend "
                    "will be connected here."
                )


            st.markdown(response)


            if show_sources:

                st.caption(
                    "📚 Source: RAG backend"
                )


            if show_confidence:

                st.caption(
                    "🎯 Confidence: --"
                )


        # ----------------------------------------------------
        # Save assistant response
        # ----------------------------------------------------

        current_chat["messages"].append(
            {
                "role": "assistant",
                "content": response,
                "source": "RAG backend",
                "confidence": "--"
            }
        )


        st.rerun()