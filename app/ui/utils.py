"""Session state: conversations, navigation, quiz + preferences."""

from datetime import datetime
from typing import Optional

import streamlit as st


# ============================================================
# DEFAULT SESSION STATE
# ============================================================

DEFAULTS = {
    "chats": {},
    "current_chat": None,
    "uploaded_files": [],
    "page": "Home",
    "quiz_started": False,
    "quiz_score": None,
    "quiz_items": [],
    "show_sources": True,
    "show_confidence": True,
    "show_trace": True,
    "studied_topics": [],
}


def init_state() -> None:
    """Initialize Streamlit session state safely."""

    for key, value in DEFAULTS.items():

        if key not in st.session_state:

            if isinstance(value, (dict, list)):
                st.session_state[key] = value.copy()

            else:
                st.session_state[key] = value


# ============================================================
# CONVERSATIONS
# ============================================================

def create_new_chat() -> str:
    """Create a new conversation and make it active."""

    chat_id = (
        f"chat_{len(st.session_state.chats) + 1}_"
        f"{int(datetime.now().timestamp())}"
    )

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now().strftime("%d %b %Y · %H:%M"),
    }

    st.session_state.current_chat = chat_id
    st.session_state.page = "Chat"

    return chat_id


def get_current_chat() -> Optional[dict]:
    """Return the currently active conversation."""

    chat_id = st.session_state.current_chat

    if not chat_id:
        return None

    return st.session_state.chats.get(chat_id)


def delete_chat(chat_id: str) -> None:
    """Delete a conversation."""

    st.session_state.chats.pop(chat_id, None)

    if st.session_state.current_chat == chat_id:

        st.session_state.current_chat = (
            next(iter(st.session_state.chats), None)
        )


def goto(page: str) -> None:
    """Navigate to a UI page."""

    st.session_state.page = page


# ============================================================
# DOCUMENTS / UPLOADS
# ============================================================

def sync_uploads(files) -> None:
    """Keep uploaded-file metadata in session state."""

    st.session_state.uploaded_files = [
        {
            "name": f.name,
            "size": getattr(f, "size", 0),
        }
        for f in (files or [])
    ]


def primary_document() -> Optional[str]:
    """Return the first uploaded document name."""

    files = st.session_state.uploaded_files

    return files[0]["name"] if files else None


# ============================================================
# CHAT TITLE GENERATION
# ============================================================

# Known academic / technical topics.
#
# These give us clean titles without requiring an LLM call.
# Later, when Gemini/LangGraph is integrated, we can replace
# the generic fallback with an actual title-generation agent.

TOPIC_KEYWORDS = {

    # --------------------------------------------------------
    # COMPUTER NETWORKS
    # --------------------------------------------------------

    "three way handshake": "TCP Three-Way Handshake",
    "three-way handshake": "TCP Three-Way Handshake",
    "handshake": "TCP Three-Way Handshake",

    "connection establishment": "TCP Connection Establishment",
    "establish a connection": "TCP Connection Establishment",
    "tcp connection": "TCP Connection Establishment",

    "congestion control": "TCP Congestion Control",
    "congestion": "TCP Congestion Control",

    "sliding window": "Sliding Window Protocol",

    "flow control": "TCP Flow Control",

    "tcp": "TCP and Networking",
    "udp": "UDP and Networking",

    "dns": "DNS",
    "http": "HTTP",
    "ftp": "FTP",
    "ipv6": "IPv6",
    "ip address": "IP Addressing",

    "osi model": "OSI Model",
    "osi layers": "OSI Model",

    "computer network": "Computer Networks",
    "computer networks": "Computer Networks",
    "network": "Computer Networks",

    # --------------------------------------------------------
    # DBMS
    # --------------------------------------------------------

    "normalization": "Database Normalization",
    "normal forms": "Database Normalization",

    "functional dependency": "Functional Dependencies",

    "transaction": "Database Transactions",
    "transactions": "Database Transactions",

    "sql joins": "SQL Joins",
    "joins": "SQL Joins",

    "sql query": "SQL Queries",
    "sql queries": "SQL Queries",
    "sql": "SQL Queries",

    "foreign key": "Database Foreign Keys",
    "primary key": "Database Keys",

    "dbms": "Database Management Systems",
    "database management": "Database Management Systems",
    "database": "Database Management Systems",

    # --------------------------------------------------------
    # OPERATING SYSTEMS
    # --------------------------------------------------------

    "deadlock": "Operating System Deadlocks",
    "deadlocks": "Operating System Deadlocks",

    "cpu scheduling": "CPU Scheduling",
    "scheduling": "OS Scheduling",

    "process synchronization": "Process Synchronization",
    "synchronization": "Process Synchronization",

    "memory management": "OS Memory Management",
    "paging": "OS Paging",
    "segmentation": "OS Segmentation",

    "process": "OS Processes",
    "processes": "OS Processes",

    "operating system": "Operating Systems",
    "operating systems": "Operating Systems",
    "os": "Operating Systems",

    # --------------------------------------------------------
    # DSA
    # --------------------------------------------------------

    "binary search": "Binary Search",
    "linear search": "Linear Search",

    "linked list": "Linked Lists",
    "linked lists": "Linked Lists",

    "binary tree": "Binary Trees",
    "binary trees": "Binary Trees",

    "binary search tree": "Binary Search Trees",
    "bst": "Binary Search Trees",

    "graph traversal": "Graph Traversal",
    "graph": "Graph Algorithms",
    "graphs": "Graph Algorithms",

    "dynamic programming": "Dynamic Programming",

    "greedy algorithm": "Greedy Algorithms",
    "greedy": "Greedy Algorithms",

    "recursion": "Recursion",

    "stack": "Stacks",
    "stacks": "Stacks",

    "queue": "Queues",
    "queues": "Queues",

    "sorting": "Sorting Algorithms",

    "array": "Arrays",
    "arrays": "Arrays",

    "hashing": "Hashing",

    "dsa": "Data Structures & Algorithms",
    "data structures": "Data Structures",
    "data structure": "Data Structures",

    # --------------------------------------------------------
    # PROGRAMMING
    # --------------------------------------------------------

    "python": "Python Programming",
    "java": "Java Programming",
    "c programming": "C Programming",
    "c language": "C Programming",

    "javascript": "JavaScript",
    "react": "React Development",
    "node.js": "Node.js Development",
    "nodejs": "Node.js Development",

    "object oriented programming": "Object-Oriented Programming",
    "oops": "Object-Oriented Programming",
    "polymorphism": "Object-Oriented Polymorphism",
    "inheritance": "Object-Oriented Inheritance",
    "encapsulation": "Object-Oriented Encapsulation",

    # --------------------------------------------------------
    # AI / ML
    # --------------------------------------------------------

    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",

    "neural network": "Neural Networks",
    "neural networks": "Neural Networks",

    "natural language processing": "Natural Language Processing",
    "nlp": "Natural Language Processing",

    "artificial intelligence": "Artificial Intelligence",
    "generative ai": "Generative AI",

    "retrieval augmented generation": "Retrieval-Augmented Generation",
    "retrieval-augmented generation": "Retrieval-Augmented Generation",
    "rag": "Retrieval-Augmented Generation",

    "gradient descent": "Gradient Descent",
    "backpropagation": "Neural Network Backpropagation",

    # --------------------------------------------------------
    # ACADEMIC / STUDY
    # --------------------------------------------------------

    "important questions": "Important Questions",
    "important question": "Important Questions",

    "exam questions": "Exam Questions",
    "previous year questions": "Previous Year Questions",
    "pyq": "Previous Year Questions",

    "revision": "Revision",
    "summary": "Topic Summary",
    "summarise": "Topic Summary",
    "summarize": "Topic Summary",
}


# Words that normally don't contribute to a useful title.

STOP_WORDS = {
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
    "could",
    "would",
    "should",
    "will",
    "you",
    "your",
    "me",
    "my",
    "explain",
    "tell",
    "describe",
    "about",
    "please",
    "why",
    "of",
    "in",
    "to",
    "for",
    "on",
    "with",
    "from",
    "and",
    "or",
    "this",
    "that",
    "it",
    "its",
    "give",
    "get",
    "show",
    "define",
    "definition",
    "meaning",
}


def generate_chat_title(question: str) -> str:
    """
    Generate a short, clean title from the first user question.

    Examples:

        How does TCP establish a connection?
            -> TCP Connection Establishment

        Explain normalization in DBMS
            -> Database Normalization

        What is the difference between stack and queue?
            -> Stacks

        Give me important DSA questions
            -> DSA Important Questions

        OS
            -> Operating Systems
    """

    if not question:
        return "New Chat"

    low = question.lower().strip()

    # --------------------------------------------------------
    # 1. Exact short-topic inputs
    # --------------------------------------------------------

    short_map = {
        "os": "Operating Systems",
        "dbms": "Database Management Systems",
        "dsa": "Data Structures & Algorithms",
        "cn": "Computer Networks",
        "tcp": "TCP and Networking",
        "udp": "UDP and Networking",
        "sql": "SQL Queries",
        "ai": "Artificial Intelligence",
        "ml": "Machine Learning",
        "nlp": "Natural Language Processing",
        "rag": "Retrieval-Augmented Generation",
    }

    if low in short_map:
        return short_map[low]

    # --------------------------------------------------------
    # 2. Known topic detection
    # --------------------------------------------------------

    for keyword in sorted(
        TOPIC_KEYWORDS,
        key=len,
        reverse=True,
    ):

        if keyword in low:

            # Special handling for "important questions".

            if keyword in {
                "important questions",
                "important question",
            }:

                if (
                    "dsa" in low
                    or "data structure" in low
                    or "data structures" in low
                ):
                    return "DSA Important Questions"

                if "dbms" in low or "database" in low:
                    return "DBMS Important Questions"

                if (
                    "os" in low
                    or "operating system" in low
                ):
                    return "OS Important Questions"

                if (
                    "network" in low
                    or "cn" in low
                ):
                    return "Computer Networks Questions"

                return "Important Questions"

            # ------------------------------------------------
            # Summary requests
            # ------------------------------------------------

            if keyword in {
                "summary",
                "summarise",
                "summarize",
            }:

                for (
                    topic_keyword,
                    topic_title,
                ) in sorted(
                    TOPIC_KEYWORDS.items(),
                    key=lambda x: len(x[0]),
                    reverse=True,
                ):

                    if topic_keyword in {
                        "summary",
                        "summarise",
                        "summarize",
                    }:
                        continue

                    if topic_keyword in low:
                        return f"{topic_title} Summary"

                return "Study Material Summary"

            return TOPIC_KEYWORDS[keyword]

    # --------------------------------------------------------
    # 3. Generic fallback
    # --------------------------------------------------------

    # If the topic isn't in our known list, create a short
    # title from the meaningful words in the question.

    words = [
        word.strip("?!.,:;()[]{}\"'")
        for word in question.split()
    ]

    useful_words = [
        word
        for word in words
        if word
        and word.lower() not in STOP_WORDS
    ]

    # Keep the sidebar clean.
    useful_words = useful_words[:5]

    if not useful_words:
        return "New Conversation"

    # Preserve common technical acronyms.
    acronyms = {
        "tcp",
        "udp",
        "dbms",
        "dsa",
        "os",
        "sql",
        "ai",
        "ml",
        "nlp",
        "http",
        "https",
        "ftp",
        "dns",
        "ip",
        "cpu",
        "ram",
        "rom",
        "api",
        "oop",
        "oops",
    }

    title_words = []

    for word in useful_words:

        if word.lower() in acronyms:
            title_words.append(word.upper())

        else:
            title_words.append(word.capitalize())

    return " ".join(title_words)