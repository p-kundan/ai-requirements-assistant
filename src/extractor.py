import os
import re
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from docx import Document
import pandas as pd

def extract_text_from_pdf(path):
    """Extract text from regular (text-based) PDFs"""
    try:
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"❌ PDF read error: {e}")
        return ""

def extract_text_from_scanned_pdf(path):
    """Extract text from scanned PDFs using OCR"""
    try:
        pages = convert_from_path(path, dpi=300)
        ocr_texts = [pytesseract.image_to_string(p) for p in pages]
        return "\n".join(ocr_texts)
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        return ""

def extract_text_from_docx(path):
    """Extract text from .docx files"""
    try:
        doc = Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        print(f"❌ DOCX read error: {e}")
        return ""

def extract_text_from_txt(path):
    """Extract text from .txt files"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ TXT read error: {e}")
        return ""

def extract_text_from_excel(path):
    """Extract text from Excel files — merges all non-empty cells row-wise"""
    try:
        df = pd.read_excel(path, engine='openpyxl')
        return "\n".join(
            df.astype(str).apply(lambda row: ' '.join(row.dropna()), axis=1)
        )
    except Exception as e:
        print(f"❌ Excel read error: {e}")
        return ""

def clean_and_split_text(raw_text):
    """Cleans text and splits it into meaningful requirement chunks"""
    lines = raw_text.splitlines()
    merged = ""

    for line in lines:
        line = line.strip()
        if not line:
            merged += "\n"
        elif line.endswith("-"):
            merged += line[:-1]
        else:
            merged += line + " "

    # 🧠 Try to split using REQ-XXX pattern
    if merged.count("REQ-") > 1:
        split_reqs = re.split(r'(REQ-\d{3,4}:\s*)', merged)
        combined = []
        for i in range(1, len(split_reqs), 2):
            req_id = split_reqs[i].strip()
            req_text = split_reqs[i + 1].strip()
            combined.append(f"{req_id} {req_text}")
        return combined

    # 🧼 Fallback: split by empty lines
    paragraphs = [p.strip() for p in merged.split("\n") if p.strip()]
    return paragraphs

def extract_requirements(path, original_filename=None):
    """
    Main function — detects file type and extracts cleaned, split requirements.
    Accepts both physical path and original uploaded filename (for extension).
    """
    ext = os.path.splitext(original_filename or path)[1].lower()

    text = ""

    if ext == ".pdf":
        text = extract_text_from_pdf(path)
        if len(text.strip()) < 100:
            print("⚠️ PDF has low text content — attempting OCR...")
            text = extract_text_from_scanned_pdf(path)

    elif ext == ".docx":
        text = extract_text_from_docx(path)

    elif ext == ".txt":
        text = extract_text_from_txt(path)

    elif ext in [".xls", ".xlsx"]:
        text = extract_text_from_excel(path)

    else:
        raise ValueError(f"❌ Unsupported file format: {ext}")

    if not text.strip():
        print("⚠️ No usable text extracted from the file.")
        return []

    return clean_and_split_text(text)
