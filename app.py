import os
import re
import html
import time
import csv
from io import BytesIO, StringIO

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# --------------------------------------------------
# App links
# --------------------------------------------------

FEEDBACK_FORM_URL = "https://tally.so/r/pbMDpP"
GITHUB_REPO_URL = "https://github.com/CTMW13/engineernotes-ai"


# --------------------------------------------------
# Manual Daily Engineering Spark
# Later, this can be automated with RSS/news APIs.
# --------------------------------------------------

DAILY_SPARK_TITLE = "Soft robotics is changing how machines interact with the real world"
DAILY_SPARK_SUMMARY = (
    "Soft robots use flexible materials instead of rigid mechanical parts, "
    "making them useful for delicate tasks such as medical devices, search-and-rescue, "
    "and handling fragile objects."
)
DAILY_SPARK_WHY_IT_MATTERS = (
    "This matters because future robots may need to work safely around humans, "
    "move through unpredictable environments, and interact with objects without damaging them."
)
DAILY_SPARK_SOURCE_LABEL = "Manual MVP briefing"
DAILY_SPARK_SOURCE_URL = GITHUB_REPO_URL


# --------------------------------------------------
# Load API key
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", None)
    except Exception:
        api_key = None

client = OpenAI(api_key=api_key)


# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="Nexa Study",
    page_icon="⚙️",
    layout="wide"
)


# --------------------------------------------------
# Custom CSS styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        --baby-blue: #CBEFFF;
        --sky-blue: #A9DCF7;
        --deep-blue: #1E3A5F;
        --mid-blue: #274B72;
        --smoky-orange: #D9825B;
        --burnt-orange: #C96A43;
        --cream: #FFF8F1;
        --soft-white: #FFFFFF;
        --slate: #334155;
        --muted-slate: #64748B;

        --lilac: #F3E8FF;
        --lilac-strong: #E9D5FF;
        --purple-border: #C084FC;
        --purple-text: #4C1D95;

        --border-blue: rgba(30, 58, 95, 0.14);
        --border-orange: rgba(217, 130, 91, 0.22);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(169, 220, 247, 0.95), transparent 35%),
            radial-gradient(circle at top right, rgba(217, 130, 91, 0.26), transparent 34%),
            radial-gradient(circle at bottom right, rgba(233, 213, 255, 0.55), transparent 30%),
            linear-gradient(135deg, #CBEFFF 0%, #E7F6FF 42%, #FFF8F1 100%);
        color: var(--deep-blue);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    .stApp,
    .stApp p,
    .stApp span,
    .stApp label,
    .stApp div,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6 {
        color: var(--deep-blue);
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p {
        color: var(--deep-blue) !important;
    }

    .hero-card {
        padding: 2.4rem;
        border-radius: 28px;
        background:
            linear-gradient(135deg, rgba(169, 220, 247, 0.98) 0%, rgba(203, 239, 255, 0.96) 42%, rgba(217, 130, 91, 0.78) 100%);
        color: var(--deep-blue);
        box-shadow: 0 18px 45px rgba(30, 58, 95, 0.20);
        border: 1px solid rgba(255, 255, 255, 0.72);
        margin-bottom: 1.5rem;
    }

    .hero-title {
        font-size: 3.15rem;
        font-weight: 850;
        margin-bottom: 0.55rem;
        letter-spacing: -0.045em;
        color: var(--deep-blue) !important;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        line-height: 1.7;
        max-width: 830px;
        color: var(--mid-blue) !important;
    }

    .hero-badges {
        margin-top: 1.25rem;
    }

    .badge {
        display: inline-block;
        padding: 0.48rem 0.78rem;
        border-radius: 999px;
        background: rgba(255, 248, 241, 0.82);
        border: 1px solid rgba(201, 106, 67, 0.28);
        color: var(--deep-blue) !important;
        margin-right: 0.45rem;
        margin-bottom: 0.45rem;
        font-size: 0.9rem;
        font-weight: 650;
    }

    .spark-card {
        background: rgba(255, 248, 241, 0.94);
        border: 1px solid rgba(217, 130, 91, 0.24);
        border-left: 7px solid var(--smoky-orange);
        border-radius: 22px;
        padding: 1.25rem 1.35rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 12px 30px rgba(30, 58, 95, 0.10);
    }

    .spark-label {
        display: inline-block;
        background: linear-gradient(135deg, #D9825B 0%, #C96A43 100%);
        color: white !important;
        padding: 0.34rem 0.65rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
    }

    .spark-title {
        font-size: 1.25rem;
        font-weight: 850;
        color: var(--deep-blue) !important;
        margin-bottom: 0.55rem;
    }

    .spark-text {
        color: var(--slate) !important;
        line-height: 1.6;
        margin-bottom: 0.45rem;
    }

    .spark-source a {
        color: var(--burnt-orange) !important;
        font-weight: 800;
        text-decoration: none;
    }

    .spark-source a:hover {
        text-decoration: underline;
    }

    .info-card {
        background: rgba(255, 248, 241, 0.95);
        padding: 1.2rem;
        border-radius: 20px;
        border: 1px solid var(--border-orange);
        box-shadow: 0 10px 28px rgba(30, 58, 95, 0.09);
        min-height: 150px;
    }

    .info-card h3 {
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.05rem;
        color: var(--deep-blue) !important;
    }

    .info-card p {
        color: var(--slate) !important;
        font-size: 0.95rem;
        line-height: 1.55;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.90);
        padding: 0.85rem 1rem;
        border-radius: 16px;
        border: 1px solid rgba(169, 220, 247, 0.95);
        color: var(--deep-blue) !important;
        box-shadow: 0 8px 22px rgba(30, 58, 95, 0.06);
    }

    .metric-card strong {
        color: var(--burnt-orange) !important;
    }

    .premium-card {
        background: linear-gradient(135deg, rgba(243, 232, 255, 0.96) 0%, rgba(233, 213, 255, 0.94) 100%);
        padding: 0.9rem 0.95rem;
        border-radius: 16px;
        border: 1px solid rgba(192, 132, 252, 0.55);
        margin-bottom: 0.75rem;
        box-shadow: 0 8px 20px rgba(76, 29, 149, 0.07);
    }

    .premium-card-title {
        font-weight: 800;
        color: var(--purple-text) !important;
        margin-bottom: 0.25rem;
    }

    .premium-card-text {
        color: #5B5270 !important;
        font-size: 0.86rem;
        line-height: 1.35;
    }

    .contact-card {
        background: rgba(255, 248, 241, 0.94);
        padding: 1rem;
        border-radius: 18px;
        border: 1px solid rgba(217, 130, 91, 0.24);
        box-shadow: 0 10px 24px rgba(30, 58, 95, 0.07);
    }

    .contact-card a {
        color: var(--burnt-orange) !important;
        font-weight: 800;
        text-decoration: none;
    }

    .contact-card a:hover {
        text-decoration: underline;
    }

    .feedback-button {
        display: inline-block;
        margin-top: 0.8rem;
        padding: 0.72rem 1rem;
        border-radius: 14px;
        background: linear-gradient(135deg, #D9825B 0%, #C96A43 100%);
        color: white !important;
        font-weight: 850;
        text-decoration: none !important;
        box-shadow: 0 10px 22px rgba(201, 106, 67, 0.22);
    }

    .feedback-button,
    .feedback-button:visited,
    .feedback-button:link,
    .feedback-button:hover,
    .feedback-button:active {
        color: white !important;
        text-decoration: none !important;
    }

    .contact-card .feedback-button,
    .contact-card .feedback-button:visited,
    .contact-card .feedback-button:link,
    .contact-card .feedback-button:hover,
    .contact-card .feedback-button:active {
        color: white !important;
        text-decoration: none !important;
    }

    .feedback-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 28px rgba(201, 106, 67, 0.28);
    }

    .section-title {
        font-size: 1.55rem;
        font-weight: 800;
        color: var(--deep-blue) !important;
        margin-top: 1.35rem;
        margin-bottom: 0.45rem;
    }

    .section-caption {
        color: var(--muted-slate) !important;
        margin-bottom: 1rem;
    }

    .privacy-note {
        background: rgba(255, 248, 241, 0.88);
        border-left: 5px solid var(--smoky-orange);
        border-radius: 14px;
        padding: 0.9rem 1rem;
        color: var(--slate) !important;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .mini-footer {
        color: var(--muted-slate) !important;
        font-size: 0.85rem;
        margin-top: 2rem;
        text-align: center;
    }

    .mini-footer a {
        color: var(--burnt-orange) !important;
        font-weight: 800;
        text-decoration: none;
    }

    .mini-footer a:hover {
        text-decoration: underline;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #CBEFFF 0%, #E7F6FF 48%, #FFF8F1 100%);
        border-right: 1px solid rgba(30, 58, 95, 0.10);
    }

    section[data-testid="stSidebar"] * {
        color: var(--deep-blue) !important;
    }

    section[data-testid="stSidebar"] .stCaptionContainer,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: var(--muted-slate) !important;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #D9825B 0%, #C96A43 100%);
        color: white !important;
        border: none;
        border-radius: 16px;
        padding: 0.78rem 1.15rem;
        font-weight: 800;
        box-shadow: 0 10px 22px rgba(201, 106, 67, 0.25);
    }

    div.stButton > button * {
        color: white !important;
    }

    div.stButton > button:hover {
        border: none;
        color: white !important;
        transform: translateY(-1px);
        box-shadow: 0 14px 28px rgba(201, 106, 67, 0.30);
    }

    div.stDownloadButton > button {
        border-radius: 16px;
        padding: 0.72rem 1rem;
        font-weight: 750;
        border: 1px solid rgba(201, 106, 67, 0.28);
        background: rgba(255, 255, 255, 0.95) !important;
        color: var(--deep-blue) !important;
    }

    div.stDownloadButton > button * {
        color: var(--deep-blue) !important;
    }

    textarea,
    input {
        background-color: #FFFFFF !important;
        color: var(--deep-blue) !important;
        border: 1px solid rgba(30, 58, 95, 0.18) !important;
        border-radius: 16px !important;
    }

    textarea::placeholder,
    input::placeholder {
        color: var(--muted-slate) !important;
        opacity: 0.85 !important;
    }

    [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: var(--deep-blue) !important;
        border: 1px solid rgba(30, 58, 95, 0.18) !important;
        border-radius: 14px !important;
        box-shadow: none !important;
    }

    [data-baseweb="select"] span,
    [data-baseweb="select"] div {
        color: var(--deep-blue) !important;
    }

    [data-baseweb="select"] svg {
        color: var(--deep-blue) !important;
        fill: var(--deep-blue) !important;
    }

    [data-baseweb="select"] input {
        color: transparent !important;
        caret-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        width: 1px !important;
        min-width: 1px !important;
        max-width: 1px !important;
        padding: 0 !important;
        margin: 0 !important;
        opacity: 0 !important;
    }

    [data-baseweb="select"] input:focus {
        color: transparent !important;
        caret-color: transparent !important;
        outline: none !important;
        border: none !important;
        box-shadow: none !important;
        opacity: 0 !important;
    }

    [data-baseweb="select"] [data-testid="stIconMaterial"] {
        background: transparent !important;
    }

    [data-baseweb="select"] > div > div:last-child {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(30, 58, 95, 0.18) !important;
        border-radius: 14px !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] > div > div {
        background: transparent !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] input {
        opacity: 0 !important;
        color: transparent !important;
        caret-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        width: 1px !important;
        min-width: 1px !important;
        max-width: 1px !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    [data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }

    [role="listbox"] {
        background-color: #FFFFFF !important;
    }

    [role="option"] {
        background-color: #FFFFFF !important;
        color: var(--deep-blue) !important;
    }

    [role="option"]:hover {
        background-color: #CBEFFF !important;
        color: var(--deep-blue) !important;
    }

    [data-testid="stAlert"] {
        border-radius: 16px;
        color: var(--deep-blue) !important;
    }

    [data-testid="stAlert"] * {
        color: var(--deep-blue) !important;
    }

    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.78);
        border-radius: 16px;
        border: 1px solid rgba(217, 130, 91, 0.24);
        overflow: hidden;
    }

    [data-testid="stExpander"] * {
        color: var(--deep-blue) !important;
    }

    [data-testid="stExpander"] summary {
        background: linear-gradient(135deg, rgba(217, 130, 91, 0.92) 0%, rgba(201, 106, 67, 0.92) 100%) !important;
        border-radius: 14px;
        padding: 0.45rem 0.7rem !important;
    }

    [data-testid="stExpander"] summary * {
        color: white !important;
        font-weight: 800 !important;
    }

    [data-testid="stExpander"] summary:hover {
        background: linear-gradient(135deg, #D9825B 0%, #C96A43 100%) !important;
    }

    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] p,
    [data-testid="stCheckbox"] span {
        color: var(--deep-blue) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Hero section
# --------------------------------------------------

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">⚙️ Nexa Study</div>
        <div class="hero-subtitle">
            Turn messy STEM notes into clear revision packs, flashcards, quizzes,
            worked examples, and downloadable study materials.
        </div>
        <div class="hero-badges">
            <span class="badge">📐 Maths</span>
            <span class="badge">⚡ Physics</span>
            <span class="badge">🛠️ Engineering</span>
            <span class="badge">🤖 Robotics</span>
            <span class="badge">💻 Computer Science</span>
            <span class="badge">🧠 AI / ML</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Daily Engineering Spark
# --------------------------------------------------

st.markdown(
    f"""
    <div class="spark-card">
        <div class="spark-label">Daily Engineering Spark</div>
        <div class="spark-title">{DAILY_SPARK_TITLE}</div>
        <div class="spark-text">{DAILY_SPARK_SUMMARY}</div>
        <div class="spark-text"><strong>Why it matters:</strong> {DAILY_SPARK_WHY_IT_MATTERS}</div>
        <div class="spark-source">
            Source: <a href="{DAILY_SPARK_SOURCE_URL}" target="_blank">{DAILY_SPARK_SOURCE_LABEL}</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Intro cards
# --------------------------------------------------

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown(
        """
        <div class="info-card">
            <h3>1. Paste your notes</h3>
            <p>Add lecture notes, textbook extracts, rough explanations, or messy revision ideas.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_b:
    st.markdown(
        """
        <div class="info-card">
            <h3>2. Choose your format</h3>
            <p>Generate summaries, flashcards, quizzes, cheat sheets, or full revision packs.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_c:
    st.markdown(
        """
        <div class="info-card">
            <h3>3. Download your pack</h3>
            <p>Export your generated material as PDF, Markdown, or flashcard files when available.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# Sidebar settings
# --------------------------------------------------

st.sidebar.title("⚙️ Workspace")
st.sidebar.caption("Shape the revision pack before generating.")

subject = st.sidebar.selectbox(
    "Subject area",
    [
        "General Study",
        "Maths",
        "Physics",
        "Computer Science",
        "Engineering",
        "Robotics",
        "AI / Machine Learning"
    ]
)

difficulty = st.sidebar.selectbox(
    "Difficulty level",
    [
        "GCSE",
        "A-Level",
        "Foundation Year",
        "University Year 1",
        "Beginner Friendly"
    ]
)

style = st.sidebar.selectbox(
    "Output style",
    [
        "Concise",
        "Detailed",
        "Exam Revision",
        "Step-by-Step Explanation"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("🔒 Premium Preview")
st.sidebar.caption("Planned features for future memberships.")

st.sidebar.markdown(
    """
    <div class="premium-card">
        <div class="premium-card-title">🎨 PDF styling themes 🔒</div>
        <div class="premium-card-text">Choose clean STEM, exam mode, minimal, or engineering notebook layouts.</div>
    </div>
    <div class="premium-card">
        <div class="premium-card-title">📂 File uploads 🔒</div>
        <div class="premium-card-text">Upload notes, PDFs, slides, and revision sheets directly.</div>
    </div>
    <div class="premium-card">
        <div class="premium-card-title">🧾 Saved revision history 🔒</div>
        <div class="premium-card-text">Save generated packs and return to them later.</div>
    </div>
    <div class="premium-card">
        <div class="premium-card-title">⚙️ Custom study branding 🔒</div>
        <div class="premium-card-text">Personalise generated packs with preferred formatting and style.</div>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Main input area
# --------------------------------------------------

st.markdown('<div class="section-title">Create a revision pack</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Paste your notes, choose an output type, then generate your study material.</div>',
    unsafe_allow_html=True
)

left_col, right_col = st.columns([2, 1])

with left_col:
    notes = st.text_area(
        "Paste your notes here:",
        height=330,
        placeholder="Example: Ohm’s law states that current equals voltage divided by resistance. I = V / R..."
    )

    note_length = len(notes)
    word_count = len(notes.split()) if notes.strip() else 0

    if note_length == 0:
        length_label = "No notes yet"
        length_message = "Paste your notes to begin."
    elif note_length < 500:
        length_label = "Short notes"
        length_message = "Good for quick summaries or flashcards."
    elif note_length < 2500:
        length_label = "Medium notes"
        length_message = "Good length for a full revision pack."
    else:
        length_label = "Long notes"
        length_message = "Consider using a detailed or exam revision style."

    st.markdown(
        f"""
        <div class="metric-card">
            <strong>{length_label}</strong> • {word_count} words • {note_length} characters<br>
            {length_message}
        </div>
        """,
        unsafe_allow_html=True
    )

with right_col:
    output_type = st.selectbox(
        "Output type",
        [
            "Summary",
            "Flashcards",
            "Quiz Questions",
            "Full Revision Pack",
            "Practice Questions",
            "Exam Cheat Sheet"
        ]
    )

    st.info("Tip: Use Flashcards if you want CSV flashcard export.")

    demo_mode = st.checkbox("Demo mode: sample density pack")

    if demo_mode:
        st.success("Demo mode uses sample density content only.")

    with st.expander("How to get better results"):
        st.write(
            """
            - Paste enough context, not just one sentence.
            - Include formulas, examples, or mistakes you want explained.
            - Choose the correct subject and difficulty level.
            - Use **Full Revision Pack** for the most complete output.
            - Use **Flashcards** if you want CSV flashcard export.
            - Avoid pasting sensitive personal data.
            """
        )

st.markdown(
    """
    <div class="privacy-note">
        <strong>Privacy reminder:</strong> Do not paste sensitive personal information, private addresses,
        student ID numbers, medical details, passwords, or anything you would not want processed by an AI service.
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Prompt builder
# --------------------------------------------------

def build_prompt(notes, output_type, subject, difficulty, style):
    return f"""
You are Nexa Study, a study assistant for STEM students.

Create a {output_type} from the notes below.

Subject area: {subject}
Difficulty level: {difficulty}
Output style: {style}

Formatting rules:
- Use clean Markdown formatting.
- Do not use LaTeX.
- Do not use equation code.
- Do not write formulas using \\frac, \\text, \\rho, \\[...\\], or similar code.
- Write formulas in plain text.
- Use Markdown tables only when they are genuinely useful.
- Keep tables simple with short cell content.
- Use plain English variable names where possible.
- If using density symbols, write "rho" instead of the Greek symbol ρ.

Good formula examples:
Density = Mass / Volume
rho = m / V
Force = Mass × Acceleration
F = ma

Make the output:
- clear
- useful for revision
- beginner-friendly where needed
- structured with headings
- easy to copy into notes

If the notes contain a mistake, gently correct it and explain the correct version.

For a Full Revision Pack, include:
1. Key Definition
2. Main Formula
3. Symbol Meanings
4. Simple Explanation
5. Worked Example
6. Common Mistakes
7. Flashcards
8. Practice Questions
9. Quick Recap

For Flashcards, use exactly this format:
Q: question text
A: answer text

Create at least 8 flashcards if there is enough content.

For Quiz Questions, include answers underneath a separate "Answers" heading.

Notes:
{notes}
"""


# --------------------------------------------------
# Fake output for demo mode
# --------------------------------------------------

def fake_output():
    return """
# Density — Full Revision Pack

## 1. Key Definition

Density tells us how much mass is packed into a certain volume.

In simple terms:

> Density = how compact or packed together a material is.

## 2. Main Formula

Density = Mass / Volume

rho = m / V

## 3. Symbol Meanings

| Symbol | Meaning | Unit |
|---|---|---|
| rho | Density | kg/m³ |
| m | Mass | kg |
| V | Volume | m³ |

## 4. Worked Example

If a block has:

- Mass = 10 kg
- Volume = 2 m³

Then:

Density = 10 / 2

Density = 5 kg/m³

## 5. Common Mistake

A common mistake is dividing density by mass.

Wrong:

Volume = Density / Mass

Correct:

Density = Mass / Volume

## 6. Flashcards

Q: What does density measure?
A: How much mass is packed into a certain volume.

Q: What is the formula for density?
A: Density = Mass / Volume.

Q: What is the SI unit of density?
A: kg/m³.

Q: What does rho represent?
A: Density.

## 7. Practice Questions

1. A block has mass 20 kg and volume 4 m³. Find the density.
2. A liquid has mass 12 kg and volume 3 m³. Find the density.

## Answers

1. Density = 20 / 4 = 5 kg/m³
2. Density = 12 / 3 = 4 kg/m³

## 8. Quick Recap

- Density tells us how compact a material is.
- Formula: Density = Mass / Volume.
- SI unit: kg/m³.
"""


# --------------------------------------------------
# Title and filename helpers
# --------------------------------------------------

def get_document_title(text):
    lines = text.splitlines()

    for line in lines:
        line = line.strip()

        if line.startswith("# "):
            title = line[2:].strip()
            break
    else:
        title = "Nexa Study Revision Pack"

    if not title:
        title = "Nexa Study Revision Pack"

    return title


def make_safe_filename(text):
    title = get_document_title(text)

    title = title.lower()
    title = re.sub(r"[^a-z0-9]+", "_", title)
    title = title.strip("_")

    if not title:
        title = "Nexa Study Revision Pack"

    return title


# --------------------------------------------------
# Flashcard helpers
# --------------------------------------------------

def extract_flashcards(text):
    """
    Extracts flashcards written as:
    Q: question
    A: answer
    """

    flashcards = []
    current_question = None

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if line.lower().startswith("q:"):
            current_question = line[2:].strip()

        elif line.lower().startswith("a:") and current_question:
            answer = line[2:].strip()

            if current_question and answer:
                flashcards.append(
                    {
                        "front": current_question,
                        "back": answer
                    }
                )

            current_question = None

    return flashcards


def flashcards_to_csv(flashcards):
    """
    Converts flashcards into CSV format with Front and Back columns.
    """

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["Front", "Back"])

    for card in flashcards:
        writer.writerow([card["front"], card["back"]])

    return output.getvalue()


def flashcards_to_pdf(flashcards, pdf_title):
    """
    Creates a simple flashcard PDF with one card per page.
    """

    buffer = BytesIO()

    font_name = "Helvetica"
    bold_font_name = "Helvetica-Bold"

    try:
        pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
        pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
        font_name = "Arial"
        bold_font_name = "Arial-Bold"
    except Exception:
        pass

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"{pdf_title} Flashcards",
        author="Nexa Study",
        subject="AI-generated flashcards",
        creator="Nexa Study"
    )

    title_style = ParagraphStyle(
        name="FlashcardTitle",
        fontName=bold_font_name,
        fontSize=18,
        leading=22,
        spaceAfter=16,
        textColor=colors.HexColor("#1E3A5F")
    )

    label_style = ParagraphStyle(
        name="FlashcardLabel",
        fontName=bold_font_name,
        fontSize=12,
        leading=16,
        spaceAfter=6,
        textColor=colors.HexColor("#C96A43")
    )

    body_style = ParagraphStyle(
        name="FlashcardBody",
        fontName=font_name,
        fontSize=13,
        leading=18,
        spaceAfter=14,
        textColor=colors.HexColor("#334155")
    )

    story = []

    for index, card in enumerate(flashcards, start=1):
        story.append(Paragraph(f"Flashcard {index}", title_style))
        story.append(Paragraph("Front", label_style))
        story.append(Paragraph(html.escape(card["front"]), body_style))
        story.append(Spacer(1, 14))
        story.append(Paragraph("Back", label_style))
        story.append(Paragraph(html.escape(card["back"]), body_style))

        if index != len(flashcards):
            story.append(PageBreak())

    doc.build(story)

    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data


# --------------------------------------------------
# Markdown to PDF converter
# --------------------------------------------------

def convert_markdown_to_pdf(markdown_text, pdf_title):
    buffer = BytesIO()

    font_name = "Helvetica"
    bold_font_name = "Helvetica-Bold"

    try:
        pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
        pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
        font_name = "Arial"
        bold_font_name = "Arial-Bold"
    except Exception:
        pass

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=pdf_title,
        author="Nexa Study",
        subject="AI-generated STEM revision pack",
        creator="Nexa Study"
    )

    normal_style = ParagraphStyle(
        name="NormalText",
        fontName=font_name,
        fontSize=10.5,
        leading=15,
        spaceAfter=7
    )

    table_style_text = ParagraphStyle(
        name="TableText",
        fontName=font_name,
        fontSize=9.5,
        leading=12
    )

    heading1_style = ParagraphStyle(
        name="Heading1",
        fontName=bold_font_name,
        fontSize=20,
        leading=24,
        spaceBefore=8,
        spaceAfter=12
    )

    heading2_style = ParagraphStyle(
        name="Heading2",
        fontName=bold_font_name,
        fontSize=15,
        leading=19,
        spaceBefore=10,
        spaceAfter=8
    )

    heading3_style = ParagraphStyle(
        name="Heading3",
        fontName=bold_font_name,
        fontSize=12.5,
        leading=16,
        spaceBefore=8,
        spaceAfter=6
    )

    quote_style = ParagraphStyle(
        name="Quote",
        fontName=font_name,
        fontSize=10,
        leading=14,
        leftIndent=14,
        spaceBefore=6,
        spaceAfter=8
    )

    story = []

    def clean_inline_formatting(text):
        text = html.escape(text)
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        return text

    def is_table_separator(line):
        stripped = line.strip()

        if not stripped.startswith("|"):
            return False

        content = stripped.replace("|", "").replace("-", "").replace(":", "").strip()
        return content == ""

    def parse_table_row(line):
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    def make_pdf_table(table_data):
        if not table_data:
            return None

        column_count = len(table_data[0])
        usable_width = A4[0] - (4 * cm)
        column_width = usable_width / column_count
        column_widths = [column_width] * column_count

        table = Table(
            table_data,
            hAlign="LEFT",
            colWidths=column_widths,
            repeatRows=1
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))

        return table

    lines = markdown_text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            story.append(Spacer(1, 6))
            i += 1
            continue

        if line.startswith("|") and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            table_data = []

            header_cells = parse_table_row(line)
            table_data.append([
                Paragraph(f"<b>{clean_inline_formatting(cell)}</b>", table_style_text)
                for cell in header_cells
            ])

            i += 2

            while i < len(lines) and lines[i].strip().startswith("|"):
                row_cells = parse_table_row(lines[i])

                while len(row_cells) < len(header_cells):
                    row_cells.append("")

                row_cells = row_cells[:len(header_cells)]

                table_data.append([
                    Paragraph(clean_inline_formatting(cell), table_style_text)
                    for cell in row_cells
                ])

                i += 1

            pdf_table = make_pdf_table(table_data)

            if pdf_table:
                story.append(pdf_table)
                story.append(Spacer(1, 10))

            continue

        if line.startswith("# "):
            story.append(Paragraph(clean_inline_formatting(line[2:]), heading1_style))

        elif line.startswith("## "):
            story.append(Paragraph(clean_inline_formatting(line[3:]), heading2_style))

        elif line.startswith("### "):
            story.append(Paragraph(clean_inline_formatting(line[4:]), heading3_style))

        elif line.startswith("- "):
            story.append(Paragraph(clean_inline_formatting("• " + line[2:]), normal_style))

        elif line.startswith("* "):
            story.append(Paragraph(clean_inline_formatting("• " + line[2:]), normal_style))

        elif line.startswith("> "):
            story.append(Paragraph(clean_inline_formatting(line[2:]), quote_style))

        else:
            story.append(Paragraph(clean_inline_formatting(line), normal_style))

        i += 1

    doc.build(story)

    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data


# --------------------------------------------------
# Download buttons
# --------------------------------------------------

def show_download_buttons(result):
    document_title = get_document_title(result)
    base_filename = make_safe_filename(result)
    pdf_data = convert_markdown_to_pdf(result, document_title)

    flashcards = extract_flashcards(result)

    st.markdown("### Downloads")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="Download Revision Pack as PDF",
            data=pdf_data,
            file_name=f"{base_filename}.pdf",
            mime="application/pdf",
            key="download_pdf"
        )

    with col2:
        st.download_button(
            label="Download Revision Pack as Markdown",
            data=result,
            file_name=f"{base_filename}.md",
            mime="text/markdown",
            key="download_markdown"
        )

    if flashcards:
        flashcard_csv = flashcards_to_csv(flashcards)
        flashcard_pdf = flashcards_to_pdf(flashcards, document_title)

        st.markdown("### Flashcard downloads")

        flash_col1, flash_col2 = st.columns(2)

        with flash_col1:
            st.download_button(
                label="Download Flashcards as CSV",
                data=flashcard_csv,
                file_name=f"{base_filename}_flashcards.csv",
                mime="text/csv",
                key="download_flashcards_csv"
            )

        with flash_col2:
            st.download_button(
                label="Download Flashcards as PDF",
                data=flashcard_pdf,
                file_name=f"{base_filename}_flashcards.pdf",
                mime="application/pdf",
                key="download_flashcards_pdf"
            )


# --------------------------------------------------
# Generate button logic
# --------------------------------------------------

generate_clicked = st.button("Generate Revision Pack")

if generate_clicked:
    if not notes.strip() and not demo_mode:
        st.warning("Paste some notes first.")
    else:
        st.markdown('<div class="section-title">Generated result</div>', unsafe_allow_html=True)

        summary_col_1, summary_col_2, summary_col_3, summary_col_4 = st.columns(4)

        with summary_col_1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <strong>Subject</strong><br>{subject}
                </div>
                """,
                unsafe_allow_html=True
            )

        with summary_col_2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <strong>Level</strong><br>{difficulty}
                </div>
                """,
                unsafe_allow_html=True
            )

        with summary_col_3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <strong>Output</strong><br>{output_type}
                </div>
                """,
                unsafe_allow_html=True
            )

        with summary_col_4:
            st.markdown(
                """
                <div class="metric-card">
                    <strong>Exports</strong><br>PDF + Markdown + Flashcards
                </div>
                """,
                unsafe_allow_html=True
            )

        if demo_mode:
            st.success("Demo mode active: sample density pack used. No API credits used.")

            with st.status("Building sample revision pack...", expanded=True) as status:
                st.write("Reading sample notes...")
                time.sleep(0.2)
                st.write("Structuring key concepts...")
                time.sleep(0.2)
                st.write("Formatting revision pack...")
                time.sleep(0.2)
                status.update(label="Sample revision pack ready.", state="complete")

            result = fake_output()

            with st.container(border=True):
                st.markdown(result)

            show_download_buttons(result)

        else:
            st.warning("Live API mode: this may use API credits.")

            if not api_key:
                st.error("No API key found. Check your .env file.")
            else:
                prompt = build_prompt(
                    notes=notes,
                    output_type=output_type,
                    subject=subject,
                    difficulty=difficulty,
                    style=style
                )

                try:
                    with st.status("Generating your revision pack...", expanded=True) as status:
                        st.write("Reading your notes...")
                        time.sleep(0.3)

                        st.write("Finding key concepts...")
                        time.sleep(0.3)

                        st.write("Building structured revision content...")
                        response = client.responses.create(
                            model="gpt-5.5",
                            input=prompt
                        )

                        st.write("Preparing downloads...")
                        time.sleep(0.3)

                        status.update(label="Revision pack ready.", state="complete")

                    result = response.output_text

                    with st.container(border=True):
                        st.markdown(result)

                    show_download_buttons(result)

                except Exception as error:
                    st.error("Something went wrong.")
                    st.code(str(error))


# --------------------------------------------------
# Feedback and privacy sections
# --------------------------------------------------

st.markdown('<div class="section-title">Feedback & privacy</div>', unsafe_allow_html=True)

feedback_col, privacy_col = st.columns(2)

with feedback_col:
    with st.expander("Send feedback or report a bug"):
        st.markdown(
            f"""
            <div class="contact-card">
                <strong>Help improve Nexa Study</strong><br><br>
                Feedback is collected through a short form. You do not need to provide
                your name or email unless you want a reply.
                <br><br>
                <a class="feedback-button" href="{FEEDBACK_FORM_URL}" target="_blank">
                    Open feedback form
                </a>
                <br><br>
                You can also view the project on GitHub:<br>
                <a href="{GITHUB_REPO_URL}" target="_blank">
                    GitHub repository
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="margin-top: 1.1rem;">
                <strong>Useful feedback includes:</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write(
            """
            - Broken PDF, Markdown, or flashcard downloads
            - Confusing explanations
            - Missing subjects or levels
            - UI suggestions
            - Feature ideas
            """
        )

with privacy_col:
    with st.expander("Privacy notice"):
        st.write(
            """
            Nexa Study processes notes pasted into the app to generate study materials.

            Current MVP behaviour:
            - Notes are used to generate revision content.
            - Notes may be sent to an AI provider for processing.
            - The app does not intentionally store pasted notes.
            - Feedback is collected through a form rather than direct email.
            - Users should avoid entering sensitive personal information.

            Do not paste:
            - Passwords
            - Addresses
            - Student ID numbers
            - Medical or legal information
            - Private personal documents
            - Anything you would not want processed by an AI service
            """
        )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown(
    f"""
    <div class="mini-footer">
        Nexa Study MVP • Built with Python, Streamlit, OpenAI API, ReportLab, and a suspicious amount of debugging.<br>
        <a href="{FEEDBACK_FORM_URL}" target="_blank">Send anonymous feedback</a>
    </div>
    """,
    unsafe_allow_html=True
)