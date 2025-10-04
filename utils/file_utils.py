import os
import docx
from pathlib import Path
import PyPDF2

upload = "uploads"
os.makedirs(upload, exist_ok=True)

def save_file(file, filename: str) -> str:
    file_path = os.path.join(upload, filename)
    with open(file_path, "wb") as f:
        f.write(file)
    return file_path

def extract_metadata(file_path: str):
    ext = Path(file_path).suffix.lower()
    file_type = ext
    file_size = os.path.getsize(file_path)
    word_count = None

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            word_count = len(f.read().split())
    elif ext == ".docx":
        doc = docx.Document(file_path)
        word_count = sum(len(p.text.split()) for p in doc.paragraphs)
    elif ext == ".pdf":
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            word_count = len(text.split())

    return {
        "file_type": file_type,
        "file_size": file_size,
        "word_count": word_count
    }