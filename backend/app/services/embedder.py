import numpy as np
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: list[str]) -> np.ndarray:
    """Many texts → array of shape (n, 384)."""
    return _model.encode(texts).astype("float32")


def embed_query(query: str) -> np.ndarray:
    """One text → a single vector of shape (384,)."""
    return _model.encode(query).astype("float32")