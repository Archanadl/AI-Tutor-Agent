"""Reusable presentational components (pure rendering, no business logic)."""

from typing import Iterable, Optional

import streamlit as st

PIPELINE_STAGES = [
    ("retrieve", "🔍 Retrieving from your material"),
    ("grade", "🧠 Grading relevance"),
    ("web", "🌐 Web fallback"),
    ("generate", "✍️ Generating answer"),
    ("done", "✅ Done"),
]


def hero(eyebrow: str, title: str, highlight: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero fade-in">
          <div class="eyebrow">✦ {eyebrow}</div>
          <h1>{title} <span class="grad">{highlight}</span></h1>
          <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat(label: str, value: str, delta: str = "", delay: int = 1) -> None:
    st.markdown(
        f"""
        <div class="stat fade-in d{delay}">
          <div class="k">{label}</div>
          <div class="v">{value}</div>
          <div class="d">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(icon: str, title: str, body: str, delay: int = 1) -> None:
    st.markdown(
        f"""
        <div class="card fade-in d{delay}">
          <div class="ico">{icon}</div>
          <p class="t">{title}</p>
          <p class="s">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def spacer(height: int = 18) -> None:
    st.markdown(f"<div style='height:{height}px'></div>", unsafe_allow_html=True)


def source_badges(source: Optional[str], source_type: Optional[str]) -> None:
    kind = (source_type or "").upper()
    if kind == "RAG":
        chip = '<span class="badge rag">🟢 Grounded in study material</span>'
    elif kind == "WEB":
        chip = '<span class="badge web">🔵 Web search fallback</span>'
    elif kind:
        chip = f'<span class="badge none">🟠 {kind}</span>'
    else:
        chip = ""
    doc = f'<span class="badge src">📚 {source}</span>' if source else ""
    if chip or doc:
        st.markdown(f"<div>{chip}{doc}</div>", unsafe_allow_html=True)


def confidence_meter(confidence: Optional[float]) -> None:
    if confidence is None:
        return
    pct = int(round(float(confidence) * 100))
    verdict = "High" if pct >= 80 else "Moderate" if pct >= 55 else "Low"
    st.markdown(
        f"""
        <div class="meter">
          <div class="bar"><div class="fill" style="width:{pct}%"></div></div>
          <div class="lbl"><span>🎯 Confidence — {verdict}</span><span>{pct}%</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def trace_strip(trace: Iterable[str]) -> None:
    trace = list(trace or [])
    if not trace:
        return
    chips = "".join(
        f'<span class="step on">{label}</span>'
        for key, label in PIPELINE_STAGES
        if key in trace
    )
    st.markdown(f'<div class="trace">{chips}</div>', unsafe_allow_html=True)


def typing_indicator(text: str = "AI Tutor is thinking") -> None:
    st.markdown(
        f'<div class="typing"><span></span><span></span><span></span> '
        f'<span style="color:var(--muted);font-size:.85rem">{text}</span></div>',
        unsafe_allow_html=True,
    )


def skeleton(lines: int = 3) -> None:
    widths = ["100%", "92%", "76%", "84%", "60%"]
    html = "".join(
        f'<div class="skeleton" style="width:{widths[i % len(widths)]}"></div>'
        for i in range(lines)
    )
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# NEW COMPONENTS — Modern UI Overhaul
# ============================================================


def metric_card(
    icon: str,
    label: str,
    value: str,
    delta: str = "",
) -> None:
    """Modern metric card with gradient top border and hover lift."""
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="mc-icon">{icon}</div>
          <div class="mc-label">{label}</div>
          <div class="mc-value">{value}</div>
          <div class="mc-delta">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_flashcard(front: str, back: str, index: int, total: int) -> None:
    """
    Pure HTML/CSS 3D flip card.
    Flips on hover — no Streamlit re-run needed for the visual animation.
    """
    front_safe = front.replace("<", "&lt;").replace(">", "&gt;")
    back_safe = back.replace("<", "&lt;").replace(">", "&gt;")

    st.markdown(
        f"""
        <div class="flip-card">
          <div class="flip-card-inner">
            <div class="flip-card-front">
              <div class="fc-label">Question</div>
              <div class="fc-text">{front_safe}</div>
            </div>
            <div class="flip-card-back">
              <div class="fc-label">Answer</div>
              <div class="fc-text">{back_safe}</div>
            </div>
          </div>
        </div>
        <div class="flip-card-counter">Card {index + 1} of {total} · Hover to flip</div>
        """,
        unsafe_allow_html=True,
    )


def timeline_item(
    number: int,
    status: str,
    tasks: list,
    total_minutes: int,
) -> None:
    """
    Modern timeline card with status dot and task list.
    Status: 'completed', 'in_progress', or 'pending'.
    """
    status_labels = {
        "completed": ("✅ Completed", "status-completed"),
        "in_progress": ("🟡 In Progress", "status-in_progress"),
        "pending": ("⬜ Pending", "status-pending"),
    }
    label, css_class = status_labels.get(status, ("⬜ Pending", "status-pending"))

    tasks_html = ""
    for task in tasks:
        topic = task.get("topic", "Study topic")
        desc = task.get("description", "")
        dur = task.get("duration_minutes", 0)
        tasks_html += f"""
        <div class="tl-task">
          <span class="tl-task-topic">{topic}</span>
          <span class="tl-task-dur"> — {dur} min</span>
          {"<div class='tl-task-desc'>" + desc + "</div>" if desc else ""}
        </div>
        """

    st.markdown(
        f"""
        <div class="timeline-item {status}">
          <div class="tl-header">
            <div class="tl-title">Session {number}</div>
            <div class="tl-badge {css_class}">{label}</div>
          </div>
          {tasks_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def welcome_banner() -> None:
    """Welcome banner shown in the Chat tab when no chat is open."""
    st.markdown(
        """
        <div class="welcome-banner">
          <div class="wb-emoji">🎓</div>
          <h2>Study with a tutor that actually <span class="grad">reads your material.</span></h2>
          <p class="wb-sub">
            Upload your notes and textbooks in the sidebar, then ask anything.
            Every answer shows where it came from, how confident the tutor is,
            and which agents ran.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
