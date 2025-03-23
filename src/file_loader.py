# src/file_loader.py

import os
import pandas as pd
from docx import Document
from PyPDF2 import PdfReader

def extract_text_from_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    return [page.extract_text() for page in reader.pages if page.extract_text()]

def extract_text_from_docx(path):
    doc = Document(path)
    return [para.text for para in doc.paragraphs if para.text.strip()]

def extract_text_from_excel(path):
    df = pd.read_excel(path, engine="openpyxl")
    return df.astype(str).apply(lambda row: ' '.join(row.dropna()), axis=1).tolist()

def load_requirements(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        return extract_text_from_txt(file_path)
    elif ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".xlsx":
        return extract_text_from_excel(file_path)
    else:
        raise ValueError(f"❌ Unsupported file format: {ext}")
