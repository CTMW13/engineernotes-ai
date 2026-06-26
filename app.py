import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from io import BytesIO
import re
import html

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Load the API key from the .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Create the OpenAI client
client = OpenAI(api_key=api_key)

# Page setup
st.set_page_config(
    page_title="EngineerNotes AI",
    page_icon="⚙️",
    layout="centered"
)

# App title
st.title("⚙️ EngineerNotes AI")
st.caption("Turn messy notes into clean revision packs for maths, physics, engineering, computer science, and robotics.")

# Sidebar settings
st.sidebar.title("Settings")

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

def build_prompt(notes, output_type, subject, difficulty, style):
    return f"""
You are EngineerNotes AI, a study assistant for students.

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
"""

if st.button("Generate"):
    if not notes.strip() and not test_mode:
        st.warning("Paste some notes first.")
    else:
        st.subheader("Result")

        if test_mode:
            result = fake_output()
            st.markdown(result)

            st.download_button(
                label="Download as Markdown",
                data=result,
                file_name="engineernotes_revision_pack.md",
                mime="text/markdown"
            )

        else:
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

                    st.markdown(result)

                    st.download_button(
                        label="Download as Markdown",
                        data=result,
                        file_name="engineernotes_revision_pack.md",
                        mime="text/markdown"
                    )

                except Exception as error:
                    st.error("Something went wrong.")
                    st.code(str(error))