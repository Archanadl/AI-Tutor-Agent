"""Global theme + CSS/animation layer for the AI Tutor UI."""

from string import Template

import streamlit as st


# ---------------------------------------------------------------------------
# Theme presets
# ---------------------------------------------------------------------------

THEMES = {
    "Midnight Aurora": {
        "bg": "#0b1020",
        "bg_soft": "#101733",
        "surface": "rgba(255,255,255,0.045)",
        "surface_strong": "rgba(255,255,255,0.08)",
        "border": "rgba(255,255,255,0.10)",
        "text": "#eaf0ff",
        "muted": "#9aa8c7",
        "primary": "#6ee7b7",
        "primary_2": "#38bdf8",
        "accent": "#f0abfc",
        "warn": "#fbbf24",
        "danger": "#fb7185",

        # Theme-specific widget colors
        "input_bg": "#111a35",
        "input_text": "#eaf0ff",
        "placeholder": "#8492b5",
        "dropdown_bg": "#111a35",
        "dropdown_hover": "#1b294d",
        "code_bg": "#111a35",
        "button_text": "#eaf0ff",
        "primary_button_text": "#04211a",
    },

    "Solar Flare": {
        "bg": "#1a0f0a",
        "bg_soft": "#241610",
        "surface": "rgba(255,255,255,0.05)",
        "surface_strong": "rgba(255,255,255,0.09)",
        "border": "rgba(255,255,255,0.12)",
        "text": "#fff3ea",
        "muted": "#c9a68f",
        "primary": "#fb923c",
        "primary_2": "#f87171",
        "accent": "#fde047",
        "warn": "#fbbf24",
        "danger": "#f87171",

        "input_bg": "#2a1a13",
        "input_text": "#fff3ea",
        "placeholder": "#c19b83",
        "dropdown_bg": "#2a1a13",
        "dropdown_hover": "#40271c",
        "code_bg": "#2a1a13",
        "button_text": "#fff3ea",
        "primary_button_text": "#2a1105",
    },

    "Forest Deep": {
        "bg": "#0a1410",
        "bg_soft": "#0f1e18",
        "surface": "rgba(255,255,255,0.045)",
        "surface_strong": "rgba(255,255,255,0.08)",
        "border": "rgba(255,255,255,0.10)",
        "text": "#eafff3",
        "muted": "#93b8a4",
        "primary": "#34d399",
        "primary_2": "#a3e635",
        "accent": "#5eead4",
        "warn": "#fbbf24",
        "danger": "#fb7185",

        "input_bg": "#10231b",
        "input_text": "#eafff3",
        "placeholder": "#83aa97",
        "dropdown_bg": "#10231b",
        "dropdown_hover": "#19352a",
        "code_bg": "#10231b",
        "button_text": "#eafff3",
        "primary_button_text": "#062b1d",
    },

    "Light Frost": {
        "bg": "#f4f7fc",
        "bg_soft": "#e9eef8",
        "surface": "#ffffff",
        "surface_strong": "#f8faff",
        "border": "#d6deec",

        # Strong dark text for readability
        "text": "#172033",
        "muted": "#52627d",

        "primary": "#0f8f8d",
        "primary_2": "#2563eb",
        "accent": "#a21caf",
        "warn": "#b45309",
        "danger": "#be123c",

        # Explicit light-theme widget colors
        "input_bg": "#ffffff",
        "input_text": "#172033",
        "placeholder": "#66758f",
        "dropdown_bg": "#ffffff",
        "dropdown_hover": "#eef3fb",
        "code_bg": "#eef3fb",
        "button_text": "#172033",
        "primary_button_text": "#ffffff",
    },
}


DEFAULT_THEME = "Midnight Aurora"

# Backwards-compatible alias
TOKENS = THEMES[DEFAULT_THEME]

FONT_SCALE = {
    "Small": "0.92",
    "Medium": "1",
    "Large": "1.12",
}


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS_TEMPLATE = Template(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=Manrope:wght@400;500;600&display=swap');


/* ============================================================
   THEME VARIABLES
   ============================================================ */

:root {
    --bg: $bg;
    --bg-soft: $bg_soft;

    --surface: $surface;
    --surface-strong: $surface_strong;
    --border: $border;

    --text: $text;
    --muted: $muted;

    --primary: $primary;
    --primary-2: $primary_2;
    --accent: $accent;

    --warn: $warn;
    --danger: $danger;

    --input-bg: $input_bg;
    --input-text: $input_text;
    --placeholder: $placeholder;

    --dropdown-bg: $dropdown_bg;
    --dropdown-hover: $dropdown_hover;

    --code-bg: $code_bg;

    --button-text: $button_text;
    --primary-button-text: $primary_button_text;

    --radius: 18px;

    --shadow:
        0 18px 50px -22px rgba(0, 0, 0, 0.35);
}


/* ============================================================
   BASE APPLICATION
   ============================================================ */

.stApp {
    background:
        radial-gradient(
            1100px 620px at 12% -10%,
            color-mix(in srgb, var(--primary-2) 18%, transparent),
            transparent 60%
        ),
        radial-gradient(
            900px 520px at 92% 0%,
            color-mix(in srgb, var(--accent) 12%, transparent),
            transparent 60%
        ),
        linear-gradient(
            180deg,
            var(--bg) 0%,
            var(--bg-soft) 100%
        );

    color: var(--text);

    font-family:
        'Manrope',
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        'Segoe UI',
        sans-serif;
}


/* ============================================================
   GLOBAL TEXT
   ============================================================ */

h1,
h2,
h3,
h4,
h5,
h6 {
    font-family:
        'Sora',
        system-ui,
        sans-serif !important;

    letter-spacing: -0.02em;

    color: var(--text) !important;
}

h1 {
    font-weight: 700 !important;
}

p,
li,
label {
    color: var(--text);
}


/* Don't blindly force every div/span to text color.
   Streamlit widgets contain internal elements where that
   can cause contrast problems. */

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: var(--text);
}


/* Captions / secondary text */

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span {
    color: var(--muted) !important;
}


/* Links */

a {
    color: var(--primary-2) !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            var(--bg-soft),
            var(--bg) 92%
        );

    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.2rem;
}

section[data-testid="stSidebar"] h1 {
    font-size: 1.35rem !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: var(--text) !important;
}

section[data-testid="stSidebar"]
[data-testid="stCaptionContainer"] p {
    color: var(--muted) !important;
}


/* ============================================================
   ALERTS
   ============================================================ */

[data-testid="stAlert"] {
    background: var(--surface-strong) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] span {
    color: var(--text) !important;
}


/* ============================================================
   EXPANDERS
   ============================================================ */

[data-testid="stExpander"] {
    border-color: var(--border) !important;
    background: var(--surface) !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: var(--text) !important;
}


/* ============================================================
   TABS
   ============================================================ */

[data-baseweb="tab"] p,
[data-baseweb="tab"] div {
    color: var(--muted) !important;
}

[data-baseweb="tab"][aria-selected="true"] p,
[data-baseweb="tab"][aria-selected="true"] div {
    color: var(--text) !important;
}


/* ============================================================
   SELECTBOX / MULTISELECT
   ============================================================ */

[data-baseweb="select"] {
    background: var(--input-bg) !important;
}

[data-baseweb="select"] > div {
    background: var(--input-bg) !important;
    color: var(--input-text) !important;

    border-color: var(--border) !important;
}

[data-baseweb="select"] div,
[data-baseweb="select"] span,
[data-baseweb="select"] input {
    color: var(--input-text) !important;
}

[data-baseweb="select"] svg {
    fill: var(--muted) !important;
}


/* Dropdown popup */

[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: var(--dropdown-bg) !important;
    border: 1px solid var(--border) !important;
}

[data-baseweb="menu"] li,
[data-baseweb="menu"] li *,
[role="option"],
[role="option"] * {
    color: var(--input-text) !important;
}

[data-baseweb="menu"] li:hover,
[role="option"]:hover {
    background: var(--dropdown-hover) !important;
}


/* ============================================================
   TEXT INPUTS
   ============================================================ */

.stTextInput input,
.stTextArea textarea {
    background: var(--input-bg) !important;
    color: var(--input-text) !important;

    border: 1px solid var(--border) !important;
    border-radius: 14px !important;

    caret-color: var(--primary) !important;
}


/* Typed text */

.stTextInput input::selection,
.stTextArea textarea::selection,
.stChatInput textarea::selection {
    background: var(--primary) !important;
    color: var(--primary-button-text) !important;
}


/* Placeholder */

.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
.stChatInput textarea::placeholder {
    color: var(--placeholder) !important;
    opacity: 1 !important;
}


/* ============================================================
   CHAT INPUT — IMPORTANT FOR LIGHT FROST
   ============================================================ */

/* Outer chat input */

[data-testid="stChatInput"] {
    background: transparent !important;
}


/* Chat input container */

[data-testid="stChatInput"] > div {
    background: var(--input-bg) !important;

    border: 1px solid var(--border) !important;

    border-radius: 16px !important;

    box-shadow:
        0 8px 30px -20px rgba(0, 0, 0, 0.45);
}


/* Actual textarea */

[data-testid="stChatInput"] textarea {
    background: var(--input-bg) !important;

    color: var(--input-text) !important;

    -webkit-text-fill-color: var(--input-text) !important;

    caret-color: var(--primary) !important;

    border: none !important;

    outline: none !important;
}


/* Chat input placeholder */

[data-testid="stChatInput"] textarea::placeholder {
    color: var(--placeholder) !important;

    -webkit-text-fill-color: var(--placeholder) !important;

    opacity: 1 !important;
}


/* Chat input icons */

[data-testid="stChatInput"] button {
    color: var(--primary) !important;
}

[data-testid="stChatInput"] button svg {
    fill: var(--primary) !important;
}


/* ============================================================
   FILE UPLOADER
   ============================================================ */

[data-testid="stFileUploaderDropzone"] {
    background: var(--surface) !important;

    border: 1.5px dashed var(--primary) !important;

    border-radius: 16px;

    transition:
        border-color .25s,
        background .25s;
}

[data-testid="stFileUploaderDropzone"]:hover {
    background: var(--surface-strong) !important;

    border-color: var(--primary-2) !important;
}


/* File uploader internal text */

[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {
    color: var(--text) !important;
}


/* Upload button */

[data-testid="stFileUploaderDropzone"] button {
    background: var(--surface-strong) !important;

    color: var(--text) !important;

    border: 1px solid var(--border) !important;
}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    width: 100%;

    border-radius: 13px;

    border: 1px solid var(--border);

    background: var(--surface);

    color: var(--button-text) !important;

    font-weight: 600;

    padding: .55rem .8rem;

    transition:
        transform .18s,
        border-color .18s,
        background .18s,
        box-shadow .25s;
}

.stButton > button:hover {
    transform: translateY(-2px);

    border-color: var(--primary) !important;

    background: var(--surface-strong) !important;

    color: var(--button-text) !important;

    box-shadow:
        0 12px 26px -18px
        color-mix(in srgb, var(--primary) 70%, transparent);
}

.stButton > button:active {
    transform: translateY(0) scale(.985);
}


/* Primary button */

.stButton > button[kind="primary"] {
    background:
        linear-gradient(
            90deg,
            var(--primary),
            var(--primary-2)
        ) !important;

    color: var(--primary-button-text) !important;

    border-color: transparent !important;
}


/* ============================================================
   CHECKBOX
   ============================================================ */

[data-testid="stCheckbox"] label {
    color: var(--text) !important;
}

[data-testid="stCheckbox"] label p,
[data-testid="stCheckbox"] label span {
    color: var(--text) !important;
}


/* ============================================================
   RADIO
   ============================================================ */

[data-testid="stRadio"] label {
    color: var(--text) !important;
}

[data-testid="stRadio"] label p,
[data-testid="stRadio"] label span {
    color: var(--text) !important;
}


/* ============================================================
   SLIDER
   ============================================================ */

[data-testid="stSlider"] label,
[data-testid="stSlider"] label p,
[data-testid="stSlider"] label span {
    color: var(--text) !important;
}

[data-testid="stTickBarMin"],
[data-testid="stTickBarMax"],
[data-testid="stThumbValue"] {
    color: var(--muted) !important;
}


/* ============================================================
   DATE INPUT
   ============================================================ */

[data-testid="stDateInput"] input {
    background: var(--input-bg) !important;

    color: var(--input-text) !important;

    -webkit-text-fill-color: var(--input-text) !important;

    border-color: var(--border) !important;
}


/* ============================================================
   METRICS
   ============================================================ */

[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stMetricDelta"] {
    color: var(--text) !important;
}


/* ============================================================
   CHAT MESSAGES
   ============================================================ */

[data-testid="stChatMessage"] {
    background: var(--surface);

    border: 1px solid var(--border);

    border-radius: 16px;

    padding: 14px 16px;

    margin-bottom: 10px;

    backdrop-filter: blur(10px);

    animation:
        floatUp .45s
        cubic-bezier(.2,.7,.2,1)
        both;
}


/* Chat message text */

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: var(--text);
}


/* ============================================================
   PROGRESS BAR
   ============================================================ */

.stProgress > div > div > div > div {
    background:
        linear-gradient(
            90deg,
            var(--primary),
            var(--primary-2)
        );
}


/* ============================================================
   CODE BLOCKS
   ============================================================ */

[data-testid="stCodeBlock"] {
    background: var(--code-bg) !important;

    border: 1px solid var(--border) !important;
}


/* ============================================================
   DIVIDERS
   ============================================================ */

hr {
    border-color: var(--border) !important;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {
    position: relative;

    overflow: hidden;

    padding: 34px 34px 30px;

    border: 1px solid var(--border);

    border-radius: 26px;

    background:
        linear-gradient(
            135deg,
            color-mix(
                in srgb,
                var(--primary) 12%,
                transparent
            ),
            color-mix(
                in srgb,
                var(--primary-2) 10%,
                transparent
            ) 40%,
            color-mix(
                in srgb,
                var(--accent) 10%,
                transparent
            )
        ),
        var(--surface);

    box-shadow: var(--shadow);

    backdrop-filter: blur(14px);
}

.hero .eyebrow {
    display: inline-flex;

    gap: 8px;

    align-items: center;

    font-size: .74rem;

    letter-spacing: .16em;

    text-transform: uppercase;

    color: var(--muted);

    border: 1px solid var(--border);

    padding: 6px 12px;

    border-radius: 999px;

    background: var(--surface-strong);
}

.hero h1 {
    margin: .6rem 0 .35rem;

    font-size: 2.5rem;

    line-height: 1.08;
}

.hero p {
    color: var(--muted) !important;

    max-width: 60ch;

    margin: 0;
}


/* ============================================================
   GRADIENT HEADING
   ============================================================ */

.hero .grad {
    background:
        linear-gradient(
            90deg,
            var(--primary),
            var(--primary-2),
            var(--accent),
            var(--primary)
        );

    background-size: 200% auto;

    -webkit-background-clip: text;

    background-clip: text;

    -webkit-text-fill-color: transparent;

    animation:
        gradientPan 7s linear infinite;
}


/* ============================================================
   CARDS
   ============================================================ */

.card {
    border: 1px solid var(--border);

    border-radius: var(--radius);

    padding: 18px 20px;

    background: var(--surface);

    backdrop-filter: blur(12px);

    box-shadow: var(--shadow);

    transition:
        transform .28s,
        border-color .28s,
        background .28s;

    height: 100%;
}

.card:hover {
    transform: translateY(-4px);

    border-color: var(--primary);

    background: var(--surface-strong);
}

.card .t {
    font-family: 'Sora', sans-serif;

    font-weight: 600;

    font-size: 1rem;

    margin: 0 0 6px;

    color: var(--text);
}

.card .s {
    color: var(--muted);

    font-size: .9rem;

    margin: 0;

    line-height: 1.5;
}

.card .ico {
    font-size: 1.4rem;
}


/* ============================================================
   STAT CARDS
   ============================================================ */

.stat {
    border: 1px solid var(--border);

    border-radius: 16px;

    padding: 16px 18px;

    background:
        linear-gradient(
            160deg,
            var(--surface-strong),
            transparent 80%
        );

    transition:
        transform .28s,
        box-shadow .28s;
}

.stat:hover {
    transform: translateY(-3px);

    box-shadow:
        0 16px 34px -22px
        color-mix(
            in srgb,
            var(--primary-2) 70%,
            transparent
        );
}

.stat .k {
    font-size: .75rem;

    letter-spacing: .1em;

    text-transform: uppercase;

    color: var(--muted);
}

.stat .v {
    font-family: 'Sora', sans-serif;

    font-size: 1.7rem;

    font-weight: 700;

    margin-top: 4px;

    color: var(--text);
}

.stat .d {
    font-size: .78rem;

    color: var(--primary);
}


/* ============================================================
   BADGES
   ============================================================ */

.badge {
    display: inline-flex;

    align-items: center;

    gap: 6px;

    font-size: .76rem;

    font-weight: 600;

    padding: 5px 11px;

    border-radius: 999px;

    border: 1px solid var(--border);

    background: var(--surface-strong);

    margin: 4px 6px 0 0;
}

.badge.rag {
    color: #062e21;

    background:
        linear-gradient(
            90deg,
            #6ee7b7,
            #34d399
        );

    border-color: transparent;
}

.badge.web {
    color: #04283a;

    background:
        linear-gradient(
            90deg,
            #7dd3fc,
            #38bdf8
        );

    border-color: transparent;
}

.badge.none {
    color: #3b2a05;

    background:
        linear-gradient(
            90deg,
            #fde68a,
            #fbbf24
        );

    border-color: transparent;
}

.badge.src {
    color: var(--muted);
}


/* ============================================================
   CONFIDENCE METER
   ============================================================ */

.meter {
    margin-top: 10px;
}

.meter .bar {
    height: 7px;

    border-radius: 999px;

    background:
        color-mix(
            in srgb,
            var(--text) 10%,
            transparent
        );

    overflow: hidden;
}

.meter .fill {
    height: 100%;

    border-radius: 999px;

    background:
        linear-gradient(
            90deg,
            var(--primary),
            var(--primary-2)
        );

    animation:
        growBar .9s
        cubic-bezier(.2,.7,.2,1)
        both;
}

.meter .lbl {
    font-size: .74rem;

    color: var(--muted);

    margin-top: 6px;

    display: flex;

    justify-content: space-between;
}


/* ============================================================
   PIPELINE
   ============================================================ */

.trace {
    display: flex;

    flex-wrap: wrap;

    gap: 8px;

    margin: 2px 0 10px;
}

.trace .step {
    font-size: .74rem;

    padding: 5px 10px;

    border-radius: 999px;

    border: 1px solid var(--border);

    background: var(--surface);

    color: var(--muted);
}

.trace .step.on {
    color: var(--text);

    border-color: var(--primary);
}


/* ============================================================
   SKELETON
   ============================================================ */

.skeleton {
    height: 14px;

    border-radius: 8px;

    margin: 8px 0;

    background:
        linear-gradient(
            90deg,
            color-mix(
                in srgb,
                var(--text) 5%,
                transparent
            ),
            color-mix(
                in srgb,
                var(--text) 12%,
                transparent
            ),
            color-mix(
                in srgb,
                var(--text) 5%,
                transparent
            )
        );

    background-size: 760px 100%;

    animation:
        shimmer 1.4s linear infinite;
}


/* ============================================================
   ANIMATIONS
   ============================================================ */

@keyframes pageIn {
    from {
        opacity: 0;
        transform: translateY(14px) scale(.995);
    }

    to {
        opacity: 1;
        transform: none;
    }
}

@keyframes floatUp {
    from {
        opacity: 0;
        transform: translateY(18px);
    }

    to {
        opacity: 1;
        transform: none;
    }
}

@keyframes shimmer {
    0% {
        background-position: -380px 0;
    }

    100% {
        background-position: 380px 0;
    }
}

@keyframes gradientPan {
    0% {
        background-position: 0% 50%;
    }

    100% {
        background-position: 200% 50%;
    }
}

@keyframes blink {
    0%,
    100% {
        opacity: .25;
    }

    50% {
        opacity: 1;
    }
}

@keyframes growBar {
    from {
        width: 0 !important;
    }
}


/* ============================================================
   PAGE LAYOUT
   ============================================================ */

#MainMenu,
footer,
header,
header [data-testid="stDecoration"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

.block-container {
    padding: 1rem 1.5rem 2rem;

    max-width: 1400px;

    animation:
        pageIn .55s
        cubic-bezier(.2,.7,.2,1);
}


/* ============================================================
   TABS — Modern Styled
   ============================================================ */

[data-baseweb="tab-list"] {
    gap: 0;

    background: var(--surface);

    border: 1px solid var(--border);

    border-radius: 16px;

    padding: 4px;

    margin-bottom: 24px;
}

[data-baseweb="tab"] {
    border-radius: 12px !important;

    padding: 10px 20px !important;

    font-weight: 600 !important;

    font-size: .92rem !important;

    transition:
        background .25s,
        color .25s,
        box-shadow .25s !important;
}

[data-baseweb="tab"]:hover {
    background: var(--surface-strong) !important;
}

[data-baseweb="tab"][aria-selected="true"] {
    background:
        linear-gradient(
            135deg,
            color-mix(in srgb, var(--primary) 20%, var(--surface-strong)),
            color-mix(in srgb, var(--primary-2) 15%, var(--surface-strong))
        ) !important;

    box-shadow:
        0 4px 16px -6px
        color-mix(in srgb, var(--primary) 40%, transparent);
}

[data-baseweb="tab"][aria-selected="true"] p,
[data-baseweb="tab"][aria-selected="true"] div {
    color: var(--text) !important;

    font-weight: 700 !important;
}

/* Hide the default tab highlight bar */
[data-baseweb="tab-highlight"] {
    display: none !important;
}

[data-baseweb="tab-border"] {
    display: none !important;
}


/* ============================================================
   METRIC CARDS — Modern Dashboard
   ============================================================ */

.metric-card {
    position: relative;

    overflow: hidden;

    border: 1px solid var(--border);

    border-radius: 20px;

    padding: 22px 24px;

    background: var(--surface);

    backdrop-filter: blur(12px);

    box-shadow:
        0 8px 32px -16px rgba(0,0,0,0.15);

    transition:
        transform .3s,
        border-color .3s,
        box-shadow .3s;
}

.metric-card::before {
    content: '';

    position: absolute;

    top: 0;
    left: 0;
    right: 0;

    height: 3px;

    background:
        linear-gradient(
            90deg,
            var(--primary),
            var(--primary-2),
            var(--accent)
        );

    border-radius: 20px 20px 0 0;
}

.metric-card:hover {
    transform: translateY(-4px);

    border-color: var(--primary);

    box-shadow:
        0 16px 40px -18px
        color-mix(in srgb, var(--primary) 50%, transparent);
}

.metric-card .mc-icon {
    font-size: 1.6rem;

    margin-bottom: 8px;
}

.metric-card .mc-label {
    font-size: .72rem;

    letter-spacing: .12em;

    text-transform: uppercase;

    color: var(--muted);

    margin-bottom: 4px;
}

.metric-card .mc-value {
    font-family: 'Sora', sans-serif;

    font-size: 2rem;

    font-weight: 700;

    color: var(--text);

    line-height: 1.1;
}

.metric-card .mc-delta {
    font-size: .8rem;

    color: var(--primary);

    margin-top: 6px;
}


/* ============================================================
   THICK PROGRESS BARS
   ============================================================ */

.stProgress > div > div > div {
    height: 12px !important;

    border-radius: 999px !important;
}

.stProgress > div > div > div > div {
    height: 12px !important;

    border-radius: 999px !important;

    background:
        linear-gradient(
            90deg,
            var(--primary),
            var(--primary-2)
        ) !important;
}


/* ============================================================
   3D FLASHCARD FLIP
   ============================================================ */

.flip-card {
    perspective: 1200px;

    width: 100%;

    height: 320px;

    cursor: pointer;
}

.flip-card-inner {
    position: relative;

    width: 100%;
    height: 100%;

    transition: transform 0.7s cubic-bezier(.4,.2,.2,1);

    transform-style: preserve-3d;
}

.flip-card:hover .flip-card-inner,
.flip-card.flipped .flip-card-inner {
    transform: rotateY(180deg);
}

.flip-card-front,
.flip-card-back {
    position: absolute;

    top: 0;
    left: 0;

    width: 100%;
    height: 100%;

    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;

    border: 1px solid var(--border);

    border-radius: 24px;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    padding: 32px;

    text-align: center;

    box-shadow:
        0 12px 40px -18px rgba(0,0,0,0.25);

    overflow: hidden;
}

.flip-card-front {
    background:
        linear-gradient(
            160deg,
            color-mix(in srgb, var(--primary) 10%, var(--surface)),
            var(--surface) 60%
        );
}

.flip-card-front::before {
    content: '❓';

    font-size: 2.5rem;

    margin-bottom: 16px;

    opacity: 0.7;
}

.flip-card-front .fc-label {
    font-size: .7rem;

    letter-spacing: .14em;

    text-transform: uppercase;

    color: var(--muted);

    margin-bottom: 12px;
}

.flip-card-front .fc-text {
    font-family: 'Sora', sans-serif;

    font-size: 1.2rem;

    font-weight: 600;

    color: var(--text);

    line-height: 1.5;
}

.flip-card-back {
    background:
        linear-gradient(
            160deg,
            color-mix(in srgb, var(--primary-2) 12%, var(--surface)),
            var(--surface) 60%
        );

    transform: rotateY(180deg);
}

.flip-card-back::before {
    content: '💡';

    font-size: 2.5rem;

    margin-bottom: 16px;

    opacity: 0.7;
}

.flip-card-back .fc-label {
    font-size: .7rem;

    letter-spacing: .14em;

    text-transform: uppercase;

    color: var(--muted);

    margin-bottom: 12px;
}

.flip-card-back .fc-text {
    font-family: 'Sora', sans-serif;

    font-size: 1.15rem;

    font-weight: 500;

    color: var(--text);

    line-height: 1.5;
}

.flip-card-counter {
    font-size: .78rem;

    color: var(--muted);

    text-align: center;

    margin-top: 10px;

    font-weight: 600;
}


/* ============================================================
   QUIZ OPTION CARDS
   ============================================================ */

.quiz-option-grid {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin: 12px 0;
}

.quiz-option {
    border: 1.5px solid var(--border);

    border-radius: 14px;

    padding: 14px 20px;

    background: var(--surface);

    cursor: pointer;

    transition:
        transform .2s,
        border-color .25s,
        background .25s,
        box-shadow .25s;

    display: flex;
    align-items: center;
    gap: 14px;

    font-size: .95rem;

    color: var(--text);
}

.quiz-option:hover {
    transform: translateX(4px);

    border-color: var(--primary);

    background: var(--surface-strong);

    box-shadow:
        0 6px 20px -10px
        color-mix(in srgb, var(--primary) 40%, transparent);
}

.quiz-option .qo-marker {
    width: 32px;
    height: 32px;

    border-radius: 10px;

    border: 1.5px solid var(--border);

    display: flex;
    align-items: center;
    justify-content: center;

    font-weight: 700;
    font-size: .85rem;

    color: var(--muted);

    flex-shrink: 0;

    transition:
        background .25s,
        border-color .25s,
        color .25s;
}

.quiz-option:hover .qo-marker {
    border-color: var(--primary);

    color: var(--primary);
}

.quiz-option.selected {
    border-color: var(--primary) !important;

    background:
        color-mix(
            in srgb,
            var(--primary) 8%,
            var(--surface)
        ) !important;
}

.quiz-option.selected .qo-marker {
    background:
        linear-gradient(
            135deg,
            var(--primary),
            var(--primary-2)
        );

    border-color: transparent;

    color: var(--primary-button-text);
}

.quiz-option.correct {
    border-color: #22c55e !important;

    background:
        color-mix(
            in srgb,
            #22c55e 10%,
            var(--surface)
        ) !important;
}

.quiz-option.correct .qo-marker {
    background: #22c55e;
    border-color: transparent;
    color: white;
}

.quiz-option.wrong {
    border-color: #ef4444 !important;

    background:
        color-mix(
            in srgb,
            #ef4444 8%,
            var(--surface)
        ) !important;
}

.quiz-option.wrong .qo-marker {
    background: #ef4444;
    border-color: transparent;
    color: white;
}


/* ============================================================
   STUDY TIMELINE
   ============================================================ */

.timeline {
    position: relative;

    padding-left: 36px;
}

.timeline::before {
    content: '';

    position: absolute;

    left: 14px;
    top: 0;
    bottom: 0;

    width: 2px;

    background:
        linear-gradient(
            180deg,
            var(--primary),
            var(--border) 70%,
            transparent
        );
}

.timeline-item {
    position: relative;

    border: 1px solid var(--border);

    border-radius: 18px;

    padding: 20px 22px;

    margin-bottom: 16px;

    background: var(--surface);

    backdrop-filter: blur(10px);

    transition:
        transform .28s,
        border-color .28s,
        box-shadow .28s;
}

.timeline-item:hover {
    transform: translateX(4px);

    border-color:
        color-mix(
            in srgb,
            var(--primary) 50%,
            var(--border)
        );

    box-shadow:
        0 8px 24px -12px rgba(0,0,0,0.15);
}

.timeline-item::before {
    content: '';

    position: absolute;

    left: -30px;
    top: 26px;

    width: 12px;
    height: 12px;

    border-radius: 50%;

    border: 2px solid var(--surface);

    background: var(--border);

    z-index: 1;
}

.timeline-item.completed::before {
    background: #22c55e;

    box-shadow: 0 0 8px rgba(34,197,94,0.5);
}

.timeline-item.in_progress::before {
    background: #f59e0b;

    box-shadow: 0 0 8px rgba(245,158,11,0.5);

    animation: blink 1.5s infinite;
}

.timeline-item.pending::before {
    background: var(--muted);
}

.timeline-item .tl-header {
    display: flex;

    align-items: center;

    justify-content: space-between;

    margin-bottom: 8px;
}

.timeline-item .tl-title {
    font-family: 'Sora', sans-serif;

    font-size: 1.05rem;

    font-weight: 600;

    color: var(--text);
}

.timeline-item .tl-badge {
    font-size: .72rem;

    font-weight: 600;

    padding: 4px 12px;

    border-radius: 999px;

    text-transform: uppercase;

    letter-spacing: .08em;
}

.tl-badge.status-completed {
    background: color-mix(in srgb, #22c55e 15%, var(--surface));

    color: #22c55e;

    border: 1px solid color-mix(in srgb, #22c55e 30%, transparent);
}

.tl-badge.status-in_progress {
    background: color-mix(in srgb, #f59e0b 15%, var(--surface));

    color: #f59e0b;

    border: 1px solid color-mix(in srgb, #f59e0b 30%, transparent);
}

.tl-badge.status-pending {
    background: var(--surface-strong);

    color: var(--muted);

    border: 1px solid var(--border);
}

.timeline-item .tl-task {
    font-size: .88rem;

    color: var(--text);

    padding: 6px 0;

    border-bottom: 1px solid
        color-mix(in srgb, var(--border) 50%, transparent);
}

.timeline-item .tl-task:last-child {
    border-bottom: none;
}

.timeline-item .tl-task-topic {
    font-weight: 600;
}

.timeline-item .tl-task-dur {
    color: var(--muted);

    font-size: .8rem;
}

.timeline-item .tl-task-desc {
    color: var(--muted);

    font-size: .78rem;

    margin-top: 2px;
}


/* ============================================================
   WELCOME BANNER (Chat empty state)
   ============================================================ */

.welcome-banner {
    text-align: center;

    padding: 48px 32px;

    border: 1px solid var(--border);

    border-radius: 26px;

    background:
        linear-gradient(
            160deg,
            color-mix(in srgb, var(--primary) 8%, var(--surface)),
            color-mix(in srgb, var(--primary-2) 6%, var(--surface)) 50%,
            color-mix(in srgb, var(--accent) 6%, var(--surface))
        );

    backdrop-filter: blur(14px);

    box-shadow: var(--shadow);

    margin-bottom: 24px;
}

.welcome-banner .wb-emoji {
    font-size: 3.5rem;

    margin-bottom: 12px;
}

.welcome-banner h2 {
    font-family: 'Sora', sans-serif !important;

    font-size: 1.8rem !important;

    margin: 0 0 8px !important;
}

.welcome-banner .wb-sub {
    color: var(--muted);

    font-size: .95rem;

    max-width: 52ch;

    margin: 0 auto;

    line-height: 1.6;
}


/* ============================================================
   RATING PILLS (Flashcard SM-2)
   ============================================================ */

.rating-pills {
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 16px;
}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 768px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        padding: 24px 20px;
    }

    .hero h1 {
        font-size: 2rem;
    }

    .flip-card {
        height: 260px;
    }

    .metric-card .mc-value {
        font-size: 1.5rem;
    }

    .timeline {
        padding-left: 28px;
    }
}

</style>
"""
)


def build_css(
    theme_name: str = DEFAULT_THEME,
    font_size: str = "Medium",
    animations_enabled: bool = True,
    density: str = "Comfortable",
) -> str:

    tokens = THEMES.get(
        theme_name,
        THEMES[DEFAULT_THEME]
    )

    css = CSS_TEMPLATE.substitute(tokens)

    scale = FONT_SCALE.get(
        font_size,
        "1"
    )

    extra = """
<style>

html,
body,
.stApp {
    font-size: %srem;
}

""" % scale

    if not animations_enabled:

        extra += """
*,
*::before,
*::after {
    animation: none !important;
    transition: none !important;
}
"""

    if density == "Compact":

        extra += """
[data-testid="stChatMessage"] {
    padding: 8px 12px;
    margin-bottom: 6px;
}

.card,
.stat {
    padding: 10px 12px;
}
"""

    extra += """
</style>
"""

    return css + extra


def inject_theme() -> None:

    theme_name = st.session_state.get(
        "theme",
        DEFAULT_THEME
    )

    font_size = st.session_state.get(
        "font_size",
        "Medium"
    )

    animations_enabled = st.session_state.get(
        "animations_enabled",
        True
    )

    density = st.session_state.get(
        "chat_density",
        "Comfortable"
    )

    st.markdown(
        build_css(
            theme_name,
            font_size,
            animations_enabled,
            density,
        ),
        unsafe_allow_html=True,
    )


def page_config() -> None:

    st.set_page_config(
        page_title="AI Tutor Agent",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded",
    )