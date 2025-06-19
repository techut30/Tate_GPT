import os
import json
import faiss
import pickle
import numpy as np
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# Paths
PROCESSED_DIR = Path("/Users/uttakarsh/Desktop/GPT Tate/data/processed")
INDEX_DIR = Path("/Users/uttakarsh/Desktop/GPT Tate/data/index")
os.makedirs(INDEX_DIR, exist_ok=True)

# Model
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

# Output files
INDEX_FILE = INDEX_DIR / "tate_faiss.index"
META_FILE = INDEX_DIR / "metadata.pkl"

# Batch size for embedding
BATCH_SIZE = 32

def load_chunks():
    files = list(PROCESSED_DIR.glob("*.json"))
    print(f"Found {len(files)} processed chunk files.")

    all_texts = []
    all_metadata = []

    for file in tqdm(files, desc="Loading chunks"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            video_id = data.get("video_id", file.stem)
            chunks = data.get("chunks", [])
            for idx, chunk in enumerate(chunks):
                all_metadata.append({
                    "video_id": video_id,
                    "chunk_index": idx,
                    "text": chunk
                })
                all_texts.append(chunk)
        except Exception as e:
            print(f"Skipped {file.name}: {e}")
    return all_texts, all_metadata

def embed_and_save(all_texts, all_metadata):
    print(f"Embedding {len(all_texts)} chunks...")

    embeddings = model.encode(
        all_texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_FILE))
    with open(META_FILE, "wb") as f:
        pickle.dump(all_metadata, f)

    print(f"Saved index to {INDEX_FILE}")
    print(f"Saved metadata to {META_FILE}")
    print(f"Total vectors indexed: {index.ntotal}")

if __name__ == "__main__":
    all_texts, all_metadata = load_chunks()
    if all_texts:
        embed_and_save(all_texts, all_metadata)
    else:
        print("No chunks found to embed.")
