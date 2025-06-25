"""
Script to encode all audio files in the dataset directory into embedding vectors
and save them for similarity search.
"""

import pickle
from pathlib import Path

from tqdm import tqdm

from src.utils.encode_audio import encode_audio, load_audio_file

# Directory paths
DATASET_DIR = Path(__file__).parent.parent / "dataset"
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)
EMBEDDINGS_PATH = OUTPUT_DIR / "embeddings.pkl"

# Supported audio file extensions
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}

def find_audio_files(dataset_dir):
    """Recursively find all audio files in the dataset directory."""
    return [f for f in dataset_dir.rglob("*") if f.suffix.lower() in AUDIO_EXTS]

def main():
    audio_files = find_audio_files(DATASET_DIR)
    print(f"Found {len(audio_files)} audio files in {DATASET_DIR}")

    embeddings = {}
    metadata = {}

    for file_path in tqdm(audio_files, desc="Encoding audio files"):
        file_id = file_path.stem  # Use filename without extension as ID
        embedding = encode_audio(str(file_path))
        if embedding is None:
            print(f"Skipping {file_path} (encoding failed)")
            continue
        # Load audio for metadata
        audio, sr, duration = load_audio_file(str(file_path))
        file_stat = file_path.stat()
        metadata[file_id] = {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "duration": duration if duration is not None else 0,
            "file_size": file_stat.st_size,
        }
        embeddings[file_id] = embedding

    # Save embeddings and metadata
    with open(EMBEDDINGS_PATH, "wb") as f:
        pickle.dump({"embeddings": embeddings, "metadata": metadata}, f)
    print(f"Saved embeddings and metadata to {EMBEDDINGS_PATH}")

if __name__ == "__main__":
    main()
