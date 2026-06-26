import os
import re
import html
import time
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# --------------------------------------------------
# App contact details
# --------------------------------------------------

CONTACT_EMAIL = "your-email@example.com"
GITHUB_REPO_URL = "https://github.com/CTMW13/engineernotes-ai"


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
    page_title="EngineerNotes AI",
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
        --baby-blue: #DFF3FF;
        --sky-blue: #B9E6FF;
        --deep-blue: #1E3A5F;
        --mid-blue: #274B72;
        --smoky-orange: #D9825B;
        --burnt-orange: #C96A43;
        --cream: #FFF8F1;
        --soft-white: #FFFFFF;
        --slate: #334155;
        --muted-slate: #64748B;
        --border-blue: rgba(30, 58, 95, 0.14);
        --border-orange: rgba(217, 130, 91, 0.22);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(185, 230, 255, 0.85), transparent 34%),
            radial-gradient(circle at top right, rgba(217, 130, 91, 0.22), transparent 32%),
            linear-gradient(135deg, #DFF3FF 0%, #EEF8FF 42%, #FFF8F1 100%);
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
            linear-gradient(135deg, rgba(185, 230, 255, 0.98) 0%, rgba(223, 243, 255, 0.96) 45%, rgba(217, 130, 91, 0.72) 100%);
        color: var(--deep-blue);
        box-shadow: 0 18px 45px rgba(30, 58, 95, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.7);
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
        background: rgba(255, 248, 241, 0.78);
        border: 1px solid rgba(201, 106, 67, 0.25);
        color: var(--deep-blue) !important;
        margin-right: 0.45rem;
        margin-bottom: 0.45rem;
        font-size: 0.9rem;
        font-weight: 650;
    }

    .info-card {
        background: rgba(255, 248, 241, 0.94);
        padding: 1.2rem;
        border-radius: 20px;
        border: 1px solid var(--border-orange);
        box-shadow: 0 10px 28px rgba(30, 58, 95, 0.08);
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
        background: rgba(255, 255, 255, 0.86);
        padding: 0.85rem 1rem;
        border-radius: 16px;
        border: 1px solid rgba(185, 230, 255, 0.9);
        color: var(--deep-blue) !important;
        box-shadow: 0 8px 22px rgba(30, 58, 95, 0.05);
    }

    .metric-card strong {
        color: var(--burnt-orange) !important;
    }

    .premium-card {
        background: rgba(255, 248, 241, 0.9);
        padding: 0.85rem 0.9rem;
        border-radius: 16px;
        border: 1px solid rgba(217, 130, 91, 0.18);
        margin-bottom: 0.7rem;
    }

    .premium-card-title {
        font-weight: 750;
        color: var(--deep-blue) !important;
        margin-bottom: 0.2rem;
    }

    .premium-card-text {
        color: var(--muted-slate) !important;
        font-size: 0.86rem;
        line-height: 1.35;
    }

    .contact-card {
        background: rgba(255, 248, 241, 0.92);
        padding: 1rem;
        border-radius: 18px;
        border: 1px solid rgba(217, 130, 91, 0.22);
        box-shadow: 0 10px 24px rgba(30, 58, 95, 0.06);
    }

    .contact-card a {
        color: var(--burnt-orange) !important;
        font-weight: 800;
        text-decoration: none;
    }

    .contact-card a:hover {
        text-decoration: underline;
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
        background: rgba(255, 248, 241, 0.86);
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

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #DFF3FF 0%, #F3FAFF 48%, #FFF8F1 100%);
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

    /* Main select box */
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

    /* Dropdown arrow */
    [data-baseweb="select"] svg {
        color: var(--deep-blue) !important;
        fill: var(--deep-blue) !important;
    }

    /* Hide the tiny input caret/rectangle inside Streamlit select boxes */
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
        background-color: #DFF3FF !important;
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
        background: rgba(255, 255, 255, 0.76);
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
        <div class="hero-title">⚙️ EngineerNotes AI</div>
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
            <p>Export your generated material as a clean PDF or Markdown file.</p>
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
        placeholder="Example: Density = mass divided by volume. SI unit is kg/m³..."
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

    st.info("Tip: Use Full Revision Pack for the most complete output.")

    test_mode = st.checkbox("Test mode: no API credits")

    if test_mode:
        st.success("Test mode uses sample content only.")

    with st.expander("How to get better results"):
        st.write(
            """
            - Paste enough context, not just one sentence.
            - Include formulas, examples, or mistakes you want explained.
            - Choose the correct subject and difficulty level.
            - Use **Full Revision Pack** for the most complete output.
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
You are EngineerNotes AI, a study assistant for STEM students.

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

For Flashcards, use this format:
Q: question
A: answer

For Quiz Questions, include answers underneath a separate "Answers" heading.

Notes:
{notes}
"""


# --------------------------------------------------
# Fake output for testing without API credits
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
        title = "EngineerNotes Revision Pack"

    if not title:
        title = "EngineerNotes Revision Pack"

    return title


def make_safe_filename(text):
    title = get_document_title(text)

    title = title.lower()
    title = re.sub(r"[^a-z0-9]+", "_", title)
    title = title.strip("_")

    if not title:
        title = "engineernotes_revision_pack"

    return title


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
        author="EngineerNotes AI",
        subject="AI-generated STEM revision pack",
        creator="EngineerNotes AI"
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

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="Download as PDF",
            data=pdf_data,
            file_name=f"{base_filename}.pdf",
            mime="application/pdf",
            key="download_pdf"
        )

    with col2:
        st.download_button(
            label="Download as Markdown",
            data=result,
            file_name=f"{base_filename}.md",
            mime="text/markdown",
            key="download_markdown"
        )


# --------------------------------------------------
# Generate button logic
# --------------------------------------------------

generate_clicked = st.button("Generate Revision Pack")

if generate_clicked:
    if not notes.strip() and not test_mode:
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
                    <strong>Exports</strong><br>PDF + Markdown
                </div>
                """,
                unsafe_allow_html=True
            )

        if test_mode:
            st.success("Test mode active: no API credits used.")

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
                <strong>Help improve EngineerNotes AI</strong><br><br>
                Send feedback, bug reports, or feature ideas by email:<br>
                <a href="mailto:{CONTACT_EMAIL}?subject=EngineerNotes%20AI%20Feedback">
                    {CONTACT_EMAIL}
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

        st.write(
            """
            Useful feedback includes:
            - Broken PDF or Markdown downloads
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
            EngineerNotes AI processes notes pasted into the app to generate study materials.

            Current MVP behaviour:
            - Notes are used to generate revision content.
            - Notes may be sent to an AI provider for processing.
            - The app does not intentionally store pasted notes.
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
        EngineerNotes AI MVP • Built with Python, Streamlit, OpenAI API, ReportLab, and a suspicious amount of debugging.<br>
        Feedback: {CONTACT_EMAIL}
    </div>
    """,
    unsafe_allow_html=True
)