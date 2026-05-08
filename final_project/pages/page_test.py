from pypdf import PdfReader
from openai import OpenAI
import os
import streamlit as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOC = ROOT / "final_project" / "LCA_structuremodis_info.pdf"

# --- Setup ---
client = OpenAI(api_key="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")

st.title("📄 AI PDF Summarizer")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

# --- Helper: extract text ---
def extract_text(DOC):
    reader = PdfReader(DOC)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# --- Helper: chunk text ---
def chunk_text(text, chunk_size=3000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# --- Helper: summarize chunk ---
def summarize_chunk(chunk):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize the following text concisely."},
            {"role": "user", "content": chunk}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

# --- Main logic ---
if uploaded_file:

    with st.spinner("Extracting text..."):
        text = extract_text(uploaded_file)

    if not text.strip():
        st.error("Could not extract text from PDF.")
        st.stop()

    st.success("Text extracted!")

    if st.button("Generate Summary"):

        chunks = chunk_text(text)

        summaries = []

        with st.spinner("Summarizing..."):
            for chunk in chunks:
                summaries.append(summarize_chunk(chunk))

        # --- Final summary ---
        final_summary = summarize_chunk(" ".join(summaries))

        st.subheader("🧠 Summary")
        st.write(final_summary)

        # Optional: expandable detailed summaries
        with st.expander("📚 Section summaries"):
            for i, s in enumerate(summaries):
                st.write(f"**Part {i+1}**")
                st.write(s)