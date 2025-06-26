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

def search_similar_tracks(query_embedding: List[float], top_k: int = 5) -> List[Dict[str, any]]:
    """
    Search for similar tracks using the query embedding.

    Args:
        query_embedding: List of floats representing the audio embedding
        top_k: Number of top similar tracks to return

    Returns:
        List of dictionaries containing track information and similarity scores
    """
    try:
        # Convert list to numpy array
        query_array = np.array(query_embedding)

        # Load embeddings and metadata
        embeddings, metadata = load_embeddings()

        if not embeddings:
            print("No embeddings found in database")
            return []

        # Perform similarity search
        results = search_similar(query_array, embeddings, top_k=top_k)

        # Format results
        formatted_results = []
        for i, (file_id, similarity_score) in enumerate(results):
            track_metadata = metadata.get(file_id, {})

            track_info = {
                "track_id": file_id,
                "title": track_metadata.get("file_name", f"Track {i+1}"),
                "artist": track_metadata.get("artist", "Unknown Artist"),
                "file_path": track_metadata.get("file_path", ""),
                "similarity_score": similarity_score,
                "metadata": track_metadata
            }
            formatted_results.append(track_info)

        return formatted_results

    except Exception as e:
        print(f"Error in similarity search: {e}")
        return []


def get_embeddings_info() -> Dict[str, any]:
    """Get information about the loaded embeddings database."""
    try:
        embeddings, metadata = load_embeddings()
        return {
            "total_tracks": len(embeddings),
            "embedding_dimension": list(embeddings.values())[0].shape[0] if embeddings else 0,
            "sample_tracks": list(metadata.keys())[:5] if metadata else []
        }
    except Exception as e:
        return {
            "error": f"Failed to load embeddings: {e}",
            "total_tracks": 0,
            "embedding_dimension": 0,
            "sample_tracks": []
        }


if __name__ == "__main__":
    # Basic test: load embeddings and perform a search
    full_embeddings, metadata = load_embeddings()
    print(f"Loaded {len(full_embeddings)} embeddings.")
    if full_embeddings:
        # Pick a random embedding as the query
        import random
        file_id = random.choice(list(full_embeddings.keys()))
        test_query_embedding = full_embeddings[file_id]
        print(f"Querying with file_id: {file_id} ({metadata[file_id]['file_name']})")
        print(f"Query embedding shape: {test_query_embedding.shape}")
        results = search_similar(test_query_embedding, full_embeddings, top_k=5)
        print("Top 5 similar files:")
        for idx, (fid, score) in enumerate(results):
            print(f"{idx+1}. {fid} ({metadata[fid]['file_name']}), score={score:.4f}")
    else:
        print("No embeddings found.")
