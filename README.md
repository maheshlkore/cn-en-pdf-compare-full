# 🇨🇳→🇺🇸 PDF Translator & Comparator

A Streamlit web app to:
- Upload a **Chinese PDF** and a **reference English PDF**
- Translate Chinese → English (OpenAI or DeepL)
- Align paragraphs and compare translations
- Export results as **Excel** or **HTML**

## 🚀 How to use on Streamlit Cloud

1. Fork or upload this repo to your own GitHub.
2. Go to [Streamlit Cloud](https://share.streamlit.io/), log in with GitHub.
3. Click **New app** → select this repo and `app.py`.
4. Add API keys in **Settings → Secrets**:

```toml
OPENAI_API_KEY="sk-xxxx"
DEEPL_API_KEY="xxxx"
```

5. Deploy! Your app will be live at:

```
https://your-app-name.streamlit.app
```

---

## 🖥 Local (optional)

If you prefer to run locally (requires Python):

```bash
pip install -r requirements.txt
streamlit run app.py
```
