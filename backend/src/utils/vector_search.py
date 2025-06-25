"""
Utility functions for loading audio embeddings and performing vector search.
"""

import pickle
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List
from sklearn.metrics.pairwise import cosine_similarity

EMBEDDINGS_PATH = Path(__file__).parent.parent.parent / "data" / "embeddings.pkl"

def load_embeddings(path: Path = EMBEDDINGS_PATH) -> Tuple[Dict[str, np.ndarray], Dict[str, dict]]:
    """Load embeddings and metadata from pickle file."""
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data["embeddings"], data["metadata"]

def search_similar(query_embedding: np.ndarray, embeddings: Dict[str, np.ndarray], top_k: int = 5) -> List[Tuple[str, float]]:
    """Find top_k most similar embeddings to the query_embedding. Returns list of (file_id, score)."""
    if not embeddings:
        return []
    keys = list(embeddings.keys())
    matrix = np.stack([embeddings[k] for k in keys])
    query = query_embedding.reshape(1, -1)
    scores = cosine_similarity(query, matrix)[0]
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [(keys[i], float(scores[i])) for i in top_indices]

if __name__ == "__main__":
    # Basic test: load embeddings and perform a search
    embeddings, metadata = load_embeddings()
    print(f"Loaded {len(embeddings)} embeddings.")
    if embeddings:
        # Pick a random embedding as query
        import random
        file_id = random.choice(list(embeddings.keys()))
        query_embedding = embeddings[file_id]
        print(f"Querying with file_id: {file_id} ({metadata[file_id]['file_name']})")
        print(f"Query embedding shape: {query_embedding.shape}")
        results = search_similar(query_embedding, embeddings, top_k=5)
        print("Top 5 similar files:")
        for idx, (fid, score) in enumerate(results):
            print(f"{idx+1}. {fid} ({metadata[fid]['file_name']}), score={score:.4f}")
    else:
        print("No embeddings found.")
