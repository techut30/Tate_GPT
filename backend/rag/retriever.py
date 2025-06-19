import faiss
import pickle
import numpy as np
from pathlib import Path
from typing import List, Tuple
from sentence_transformers import SentenceTransformer

# Correct directory paths from your system
INDEX_DIR = Path("/Users/uttakarsh/Desktop/GPT Tate/data/index")
INDEX_FILE = INDEX_DIR / "tate_faiss.index"
META_FILE = INDEX_DIR / "metadata.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

# Load model
model = SentenceTransformer(MODEL_NAME)

# Load index and metadata
index = faiss.read_index(str(INDEX_FILE))
with open(META_FILE, "rb") as f:
    metadata = pickle.load(f)

def embed_query(query: str) -> np.ndarray:
    """Embed the input query using same model as chunks."""
    return model.encode([query], convert_to_numpy=True)

def search(query: str, top_k: int = 5) -> List[Tuple[str, str]]:
    """Search the FAISS index and return top_k (text, video_id) pairs."""
    query_vector = embed_query(query)
    scores, indices = index.search(query_vector, top_k)

    results = []
    for idx in indices[0]:
        # Handle invalid indices
        if idx >= 0 and idx < len(metadata):
            item = metadata[idx]
            results.append((item["text"], item["video_id"]))
    return results
