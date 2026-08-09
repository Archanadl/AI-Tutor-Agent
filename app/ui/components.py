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
