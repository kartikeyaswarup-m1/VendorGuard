import fitz
import os
import re
from hashlib import sha256

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def extract_text_chunks(pdf_path, min_len=20, max_len=1200):
    try:
        doc = fitz.open(pdf_path)
    except Exception:
        return []
    chunks = []
    for page_no in range(len(doc)):
        page = doc.load_page(page_no)
        text = page.get_text("text")
        if not text or not text.strip():
            continue
        parts = re.split(r"\n{2,}|\.\s+", text)
        idx = 0
        for part in parts:
            part = part.strip()
            if len(part) < min_len:
                continue
            while len(part) > max_len:
                chunk = part[:max_len]
                last = chunk.rfind(". ")
                if last > int(max_len*0.6):
                    chunk = chunk[:last+1]
                h = sha256(chunk.encode("utf8")).hexdigest()
                chunks.append({"page": page_no+1, "chunk_index": idx, "text": chunk, "clause_hash": h})
                part = part[len(chunk):].strip()
                idx += 1
            if part:
                h = sha256(part.encode("utf8")).hexdigest()
                chunks.append({"page": page_no+1, "chunk_index": idx, "text": part, "clause_hash": h})
                idx += 1
    return chunks