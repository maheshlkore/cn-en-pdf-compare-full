import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import openai
import deepl
import difflib
from io import BytesIO

# ----------------------------
# Streamlit page config
# ----------------------------
st.set_page_config(page_title="Chinese → English PDF Translator & Comparator", layout="wide")

st.title("🇨🇳 → 🇺🇸 PDF Translator & Comparator")
st.write("Upload a **Chinese PDF** and an **English PDF**, translate, and compare results.")

# ----------------------------
# Helper: Extract text from PDF
# ----------------------------
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text_blocks = []
    for page in doc:
        text = page.get_text("text")
        if text.strip():
            text_blocks.append(text.strip())
    return text_blocks

# ----------------------------
# Translation functions
# ----------------------------
def translate_openai(ch_text, api_key):
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a translator from Chinese to English."},
                {"role": "user", "content": ch_text},
            ],
            temperature=0
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[OpenAI Error: {e}]"

def translate_deepl(ch_text, api_key):
    try:
        translator = deepl.Translator(api_key)
        result = translator.translate_text(ch_text, target_lang="EN-US")
        return result.text
    except Exception as e:
        return f"[DeepL Error: {e}]"

# ----------------------------
# Sidebar configuration
# ----------------------------
st.sidebar.header("⚙️ Settings")

engine = st.sidebar.radio("Translation Engine", ["OpenAI", "DeepL"])
openai_key = st.sidebar.text_input("OpenAI API Key", type="password") if engine == "OpenAI" else None
deepl_key = st.sidebar.text_input("DeepL API Key", type="password") if engine == "DeepL" else None

# ----------------------------
# File uploads
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    cn_pdf = st.file_uploader("Upload Chinese PDF", type="pdf")

with col2:
    en_pdf = st.file_uploader("Upload Reference English PDF", type="pdf")

# ----------------------------
# Main workflow
# ----------------------------
if st.button("🚀 Translate & Compare"):
    if not cn_pdf or not en_pdf:
        st.error("Please upload both PDFs before proceeding.")
    elif engine == "OpenAI" and not openai_key:
        st.error("Please provide your OpenAI API key.")
    elif engine == "DeepL" and not deepl_key:
        st.error("Please provide your DeepL API key.")
    else:
        st.info("⏳ Processing PDFs... this may take a while for large files.")

        # Extract
        chinese_texts = extract_text_from_pdf(cn_pdf)
        english_texts = extract_text_from_pdf(en_pdf)

        # Translate Chinese paragraphs
        translations = []
        for i, ch in enumerate(chinese_texts, start=1):
            st.write(f"Translating paragraph {i}/{len(chinese_texts)}...")
            if engine == "OpenAI":
                tr = translate_openai(ch, openai_key)
            else:
                tr = translate_deepl(ch, deepl_key)
            translations.append(tr)

        # Align into DataFrame
        df = pd.DataFrame({
            "Chinese Text": chinese_texts,
            "Machine Translation": translations,
            "Reference English": english_texts[:len(translations)]
        })

        # Compute similarity
        similarities = []
        for mt, ref in zip(df["Machine Translation"], df["Reference English"]):
            seq = difflib.SequenceMatcher(None, mt, ref)
            similarities.append(round(seq.ratio() * 100, 2))
        df["Similarity %"] = similarities

        st.success("✅ Translation & comparison complete!")

        # Show results
        st.dataframe(df, use_container_width=True)

        # Download Excel
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        st.download_button(
            label="📥 Download Excel",
            data=excel_buffer.getvalue(),
            file_name="translation_comparison.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Download HTML
        html_buffer = BytesIO()
        df.to_html(html_buffer, index=False)
        st.download_button(
            label="📥 Download HTML Report",
            data=html_buffer.getvalue(),
            file_name="translation_comparison.html",
            mime="text/html"
        )
