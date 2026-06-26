import os
import re
import html
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
# Load API key
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# This helps later if you deploy to Streamlit Cloud
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
    layout="centered"
)

st.title("⚙️ EngineerNotes AI")
st.caption(
    "Turn messy STEM notes into clean revision packs for maths, physics, "
    "engineering, computer science, robotics, and AI."
)


# --------------------------------------------------
# Sidebar settings
# --------------------------------------------------

st.sidebar.title("⚙️ Settings")

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

st.sidebar.subheader("🔒 Premium Features")
st.sidebar.caption("Coming soon.")

premium_enabled = False

st.sidebar.checkbox(
    "PDF styling themes 🔒",
    disabled=not premium_enabled
)

st.sidebar.checkbox(
    "File uploads 🔒",
    disabled=not premium_enabled
)

st.sidebar.checkbox(
    "Saved revision history 🔒",
    disabled=not premium_enabled
)


# --------------------------------------------------
# Main input area
# --------------------------------------------------

output_type = st.selectbox(
    "What do you want to create?",
    [
        "Summary",
        "Flashcards",
        "Quiz Questions",
        "Full Revision Pack",
        "Practice Questions",
        "Exam Cheat Sheet"
    ]
)

notes = st.text_area(
    "Paste your notes here:",
    height=300,
    placeholder="Example: Density = mass divided by volume. SI unit is kg/m³..."
)

test_mode = st.checkbox("Test formatting without using API credits")


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

Good formula examples:
Density = Mass / Volume
ρ = m / V
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

ρ = m / V

## 3. Symbol Meanings

| Symbol | Meaning | Unit |
|---|---|---|
| ρ | Density | kg/m³ |
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
# Markdown to PDF converter
# --------------------------------------------------

def convert_markdown_to_pdf(markdown_text):
    """
    Converts Markdown-style text into a simple downloadable PDF.
    Handles headings, bullets, quotes, and basic Markdown tables.
    """

    buffer = BytesIO()

    font_name = "Helvetica"
    bold_font_name = "Helvetica-Bold"

    # Try to use Arial on Windows for better symbol support
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
        bottomMargin=2 * cm
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
        """
        Converts simple Markdown bold into ReportLab-friendly tags.
        """
        text = html.escape(text)
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        return text

    def is_table_separator(line):
        """
        Detects Markdown table separator lines like:
        |---|---|---|
        |:---|:---:|---:|
        """
        stripped = line.strip()

        if not stripped.startswith("|"):
            return False

        content = stripped.replace("|", "").replace("-", "").replace(":", "").strip()
        return content == ""

    def parse_table_row(line):
        """
        Converts a Markdown table row into a list of cell strings.
        Example:
        | Symbol | Meaning | Unit |
        becomes:
        ["Symbol", "Meaning", "Unit"]
        """
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    def make_pdf_table(table_data):
        """
        Creates a ReportLab table from parsed Markdown table data.
        Column widths are calculated based on the number of columns.
        """

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

        # Empty line
        if not line:
            story.append(Spacer(1, 6))
            i += 1
            continue

        # Markdown table detection
        if line.startswith("|") and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            table_data = []

            # Header row
            header_cells = parse_table_row(line)
            table_data.append([
                Paragraph(f"<b>{clean_inline_formatting(cell)}</b>", table_style_text)
                for cell in header_cells
            ])

            # Skip separator row
            i += 2

            # Body rows
            while i < len(lines) and lines[i].strip().startswith("|"):
                row_cells = parse_table_row(lines[i])

                # Keep row length consistent with header length
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

        # Headings
        if line.startswith("# "):
            story.append(Paragraph(clean_inline_formatting(line[2:]), heading1_style))

        elif line.startswith("## "):
            story.append(Paragraph(clean_inline_formatting(line[3:]), heading2_style))

        elif line.startswith("### "):
            story.append(Paragraph(clean_inline_formatting(line[4:]), heading3_style))

        # Bullets
        elif line.startswith("- "):
            story.append(Paragraph(clean_inline_formatting("• " + line[2:]), normal_style))

        elif line.startswith("* "):
            story.append(Paragraph(clean_inline_formatting("• " + line[2:]), normal_style))

        # Quotes
        elif line.startswith("> "):
            story.append(Paragraph(clean_inline_formatting(line[2:]), quote_style))

        # Normal text
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
    """
    Shows both PDF and Markdown download buttons.
    """

    pdf_data = convert_markdown_to_pdf(result)

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="Download as PDF",
            data=pdf_data,
            file_name="engineernotes_revision_pack.pdf",
            mime="application/pdf"
        )

    with col2:
        st.download_button(
            label="Download as Markdown",
            data=result,
            file_name="engineernotes_revision_pack.md",
            mime="text/markdown"
        )


# --------------------------------------------------
# Generate button logic
# --------------------------------------------------

if st.button("Generate"):
    if not notes.strip() and not test_mode:
        st.warning("Paste some notes first.")
    else:
        st.subheader("Result")

        if test_mode:
            st.success("Test mode active: no API credits used.")

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
                    with st.spinner("Generating your revision pack..."):
                        response = client.responses.create(
                            model="gpt-5.5",
                            input=prompt
                        )

                    result = response.output_text

                    with st.container(border=True):
                        st.markdown(result)

                    show_download_buttons(result)

                except Exception as error:
                    st.error("Something went wrong.")
                    st.code(str(error))