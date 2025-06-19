import os
import re
import json
from pathlib import Path
from typing import List
from tqdm import tqdm

# Config
RAW_DIR = Path("/Users/uttakarsh/Desktop/Tate/data/raw")
OUT_DIR = Path("/Users/uttakarsh/Desktop/Tate/data/processed")
CHUNK_SIZE = 500  # approx chars per chunk
CHUNK_OVERLAP = 100  # overlapping characters between chunks

os.makedirs(OUT_DIR, exist_ok=True)

def clean_text(text: str) -> str:
    """Clean transcript text and remove emojis"""
    # Remove emojis and non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    # Collapse multiple newlines
    text = re.sub(r"\n+", "\n", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
        if start >= len(text):
            break
    return chunks

def preprocess_all():
    if not RAW_DIR.exists():
        print(f"Error: Raw directory not found: {RAW_DIR}")
        return

    txt_files = [f for f in RAW_DIR.iterdir() if f.suffix == ".txt"]
    print(f"Found {len(txt_files)} raw text files.")

    for file in tqdm(txt_files, desc="Processing files"):
        try:
            with open(file, "r", encoding="utf-8", errors="replace") as f:
                raw_text = f.read()

            cleaned = clean_text(raw_text)
            chunks = chunk_text(cleaned)

            video_id = file.stem
            out_path = OUT_DIR / f"{video_id}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({
                    "video_id": video_id,
                    "chunks": chunks
                }, f, indent=2)

            print(f"Processed {video_id}: {len(chunks)} chunks -> {out_path}")
        except Exception as e:
            print(f"Skipped {file.name}: {e}")

if __name__ == "__main__":
    preprocess_all()
