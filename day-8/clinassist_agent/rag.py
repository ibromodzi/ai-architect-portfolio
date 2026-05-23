# clinassist_agent/rag.py
# Local RAG pipeline using sentence-transformers + FAISS.
# No cloud account required. Replace with VertexAiRagRetrieval
# when deploying to Cloud Run on Day 13.

import json
import os
from pathlib import Path
from typing import Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge_base"
INDEX_PATH = Path(__file__).parent / "faiss.index"
METADATA_PATH = Path(__file__).parent / "faiss_metadata.json"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # small, fast, runs on CPU
CHUNK_SIZE = 400  # characters per chunk (approx 100 tokens)
CHUNK_OVERLAP = 80  # overlap to avoid losing context at boundaries
TOP_K = 3  # number of chunks to retrieve per query

# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def chunk_text(
    text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[str]:
    """Splits text into overlapping character-level chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start += size - overlap

    return [c for c in chunks if len(c) > 50]  # drop tiny trailing chunks


# ---------------------------------------------------------------------------
# Build index
# ---------------------------------------------------------------------------


def build_index(force_rebuild: bool = False) -> None:
    """Reads all .txt files in KNOWLEDGE_DIR, chunks them, embeds them with

    sentence-transformers, and stores the FAISS index and metadata to disk.
    Skips rebuild if index already exists.
    """
    if INDEX_PATH.exists() and METADATA_PATH.exists() and not force_rebuild:
        print("[RAG] Index already exists. Skipping rebuild.")
        return

    print("[RAG] Building index...")

    model = SentenceTransformer(EMBEDDING_MODEL)
    chunks = []
    metadata = []  # parallel list: {source, chunk_index, text}

    for txt_file in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        content = txt_file.read_text(encoding="utf-8")
        file_chunks = chunk_text(content)
        for i, chunk in enumerate(file_chunks):
            chunks.append(chunk)
            metadata.append(
                {
                    "source": txt_file.name,
                    "chunk_index": i,
                    "text": chunk,
                }
            )

    if not chunks:
        raise ValueError(
            f"No .txt files found in {KNOWLEDGE_DIR}. "
            "Add health knowledge documents before building the index."
        )

    embeddings = model.encode(
        chunks, show_progress_bar=True, convert_to_numpy=True
    ).astype("float32")
    faiss.normalize_L2(embeddings)  # cosine similarity via inner product

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))

    print(
        f"[RAG] Index built: {len(chunks)} chunks from "
        f"{len(list(KNOWLEDGE_DIR.glob('*.txt')))} files."
    )


# ---------------------------------------------------------------------------
# Retrieve
# ---------------------------------------------------------------------------
_index: Optional[faiss.Index] = None
_metadata: Optional[list[dict]] = None
_model: Optional[SentenceTransformer] = None


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """Embeds the query and returns the top_k most similar chunks from the FAISS

    index. Each result dict contains:
    - text: the chunk content
    - source: the filename it came from
    - score: cosine similarity (0-1, higher = more relevant)

    Lazily loads the index on first call.
    """
    global _index, _metadata, _model

    if _index is None:
        if not INDEX_PATH.exists():
            build_index()
        _index = faiss.read_index(str(INDEX_PATH))
        _metadata = json.loads(METADATA_PATH.read_text())
        _model = SentenceTransformer(EMBEDDING_MODEL)

    query_vec = _model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_vec)

    scores, indices = _index.search(query_vec, top_k)
    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        entry = _metadata[idx].copy()
        entry["score"] = round(float(score), 4)
        results.append(entry)

    return results