
# 🧠 AI-Powered Requirements Engineering Assistant

An intelligent, local-first assistant for extracting, classifying, validating, and linking system requirements — powered by `llama-cpp-python`, Streamlit, and local LLMs like Mistral 7B.

---

## 🚀 Features

- 📄 Upload `.docx`, `.pdf`, `.txt`, `.xlsx` requirements
- 🧠 LLM-based classification (Functional, Non-Functional, Ambiguous)
- 💬 LLM-generated explanations
- ⚠️ Ambiguity scoring via keywords and LLM
- 🔁 Traceability Matrix: Stakeholder ➡ System ➡ Test Case
- 🕸️ Interactive Network Graph
- 📤 Export all traceability data to Excel (multi-tab) or CSV
- ✅ Fully offline, privacy-first design

---

## 📁 Project Structure

```
reqAI/
├── app.py                  # Streamlit GUI
├── models/                 # .gguf LLM model (excluded from Git)
├── src/
│   ├── extractor.py        # Handles text extraction
│   ├── nlp.py              # Handles classification, scoring
│   └── traceability.py     # Trace link generation + graph
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🛠️ Setup Instructions

1. Clone this repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-requirements-assistant.git
   cd ai-requirements-assistant
   ```

2. Create virtual environment:
   ```bash
   python -m venv reqai-env
   reqai-env\Scripts\activate  # or source reqai-env/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download the `mistral-7b-instruct-v0.1.Q4_K_M.gguf` model  
   Place it in the `models/` directory.

5. Run the assistant:
   ```bash
   streamlit run app.py
   ```

---

## 📸 Screenshots

![UI Screenshot](reqAI\demo\image.png)
![UI Screenshot](reqAI\demo\image.png)
![UI Screenshot](reqAI\demo\image.png)

---

## 🔮 Roadmap

- 🧠 Add context-aware prompt tuning
- 🧾 Auto-generate PDF traceability reports
- 🧪 Integration with MBSE tools

---

## 🪄 License

MIT License. Built by [Kundan](https://github.com/p-kundan) 👨‍💻
