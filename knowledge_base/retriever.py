"""
HBNC Knowledge Base Retriever

Loads the FAISS index and metadata once at startup, provides retrieval functions
to query the knowledge base for RAG (Retrieval Augmented Generation) context.

Env vars:
    KB_INDEX_PATH     — path to faiss_index.bin (default: knowledge_base/embeddings/faiss_index.bin)
    KB_METADATA_PATH  — path to chunks_metadata.json (default: knowledge_base/embeddings/chunks_metadata.json)
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Cached index and metadata (loaded once at startup)
_faiss_index = None
_chunks_metadata = None
_embedding_model = None
_embedding_dimension = None


def _get_env_path(env_var: str, default: str) -> str:
    """Get path from environment variable or default, trying multiple search locations."""
    # Try environment variable first
    env_path = os.environ.get(env_var)
    if env_path and Path(env_path).exists():
        return env_path

    # Try default path relative to current directory
    if Path(default).exists():
        return default

    # Try path relative to knowledge_base directory
    kb_dir = Path(__file__).parent
    kb_relative = kb_dir / Path(default).name
    if kb_relative.exists():
        return str(kb_relative)

    # Try path relative to parent/knowledge_base
    parent_kb = Path(__file__).parent.parent / "knowledge_base" / Path(default).name
    if parent_kb.exists():
        return str(parent_kb)

    # Try from parent directory
    for search_dir in [Path.cwd(), Path(__file__).parent.parent, Path(__file__).parent]:
        candidate = search_dir / default
        if candidate.exists():
            return str(candidate)

    # Return default as-is (will fail with clear error later)
    return default


def load_index() -> bool:
    """
    Load FAISS index and metadata into memory.
    Returns True on success, False on failure.
    Logs warnings if embeddings directory doesn't exist (graceful fallback).
    """
    global _faiss_index, _chunks_metadata, _embedding_model, _embedding_dimension

    if _faiss_index is not None and _chunks_metadata is not None:
        return True  # Already loaded

    index_path = _get_env_path(
        "KB_INDEX_PATH",
        "knowledge_base/embeddings/faiss_index.bin"
    )
    metadata_path = _get_env_path(
        "KB_METADATA_PATH",
        "knowledge_base/embeddings/chunks_metadata.json"
    )

    # Check if paths exist
    if not Path(index_path).exists():
        print(
            f"[WARNING] FAISS index not found at {index_path}. "
            "RAG retrieval will be disabled — backend will fall back to zero-shot generation.",
            file=sys.stderr
        )
        return False

    if not Path(metadata_path).exists():
        print(
            f"[WARNING] Metadata not found at {metadata_path}. "
            "RAG retrieval will be disabled.",
            file=sys.stderr
        )
        return False

    try:
        # Load FAISS index
        import faiss
        _faiss_index = faiss.read_index(index_path)
        print(f"[OK] Loaded FAISS index from {index_path}", file=sys.stderr)

        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _chunks_metadata = data.get("chunks", [])
            _embedding_model = data.get("embedding_model", "models/gemini-embedding-001")
            _embedding_dimension = data.get("embedding_dimension", 3072)

        print(
            f"[OK] Loaded {len(_chunks_metadata)} chunks from {metadata_path}",
            file=sys.stderr
        )
        print(
            f"[OK] RAG retrieval ready: {_embedding_model} (dim={_embedding_dimension})",
            file=sys.stderr
        )
        return True

    except Exception as e:
        print(
            f"[ERROR] Failed to load knowledge base: {e}",
            file=sys.stderr
        )
        return False


def is_loaded() -> bool:
    """Check if knowledge base is loaded and ready."""
    return _faiss_index is not None and _chunks_metadata is not None


def build_rag_query(
    danger_signs: List[str],
    visit_day: Optional[int],
    baby_weight: Optional[float],
    extra_concerns: Optional[List[str]]
) -> str:
    """
    Construct a focused retrieval query from visit parameters.
    This query is used to embed and search the FAISS index for relevant chunks.

    Args:
        danger_signs: List of danger signs detected (e.g., ['feeding', 'warmth'])
        visit_day: Day of postnatal visit (e.g., 1, 3, 7, 14, 21, 28, 42)
        baby_weight: Baby weight in kg
        extra_concerns: Free-text extra concerns from ASHA

    Returns:
        A focused query string to embed for retrieval
    """
    parts = []

    # Add visit day context
    if visit_day:
        parts.append(f"day {visit_day} postnatal visit")

    # Add baby weight context (relevant for feeding, nutrition)
    if baby_weight:
        if baby_weight < 2.0:
            parts.append("low birth weight baby")
        elif baby_weight < 2.5:
            parts.append("small baby weight")
        parts.append(f"baby weight {baby_weight} kg")

    # Add danger signs (these are high-priority for retrieval)
    if danger_signs:
        danger_query = " ".join(danger_signs)
        parts.append(f"danger signs: {danger_query}")

    # Add extra concerns (free-text)
    if extra_concerns:
        concern_query = " ".join(extra_concerns)
        parts.append(f"concerns: {concern_query}")

    # If nothing specific, use a generic fallback
    if not parts:
        return "HBNC newborn care counselling advice"

    query = " ".join(parts)
    return query


def retrieve(query_text: str, top_k: int = 4) -> List[Dict]:
    """
    Retrieve top_k most relevant chunks from the knowledge base.

    Embeds the query using the same embedding model as the index, searches FAISS,
    and returns the top_k chunks with their metadata.

    Args:
        query_text: The query to embed and search
        top_k: Number of top chunks to return (default 4)

    Returns:
        List of dicts with keys: text, source, heading, chunk_id, similarity_score
        Returns empty list if KB not loaded or embedding fails.
    """
    if not is_loaded():
        return []

    try:
        import google.generativeai as genai

        # Get API key from environment
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("[WARNING] GOOGLE_API_KEY not set — cannot embed query for RAG retrieval", file=sys.stderr)
            return []

        # Configure API (reuse existing config if already done)
        try:
            genai.configure(api_key=api_key)
        except Exception:
            pass  # May already be configured

        # Embed the query using the same model and task type as the index
        query_embedding_response = genai.embed_content(
            model=_embedding_model,
            content=query_text,
            task_type="RETRIEVAL_QUERY"
        )

        query_embedding = query_embedding_response["embedding"]

        # Search FAISS index
        import numpy as np
        query_vector = np.array([query_embedding]).astype('float32')

        # FAISS IndexFlatL2 returns distances; lower is better
        distances, indices = _faiss_index.search(query_vector, top_k)
        distances = distances[0]  # Unpack single query result
        indices = indices[0]

        # Build result list
        results = []
        for i, idx in enumerate(indices):
            if 0 <= idx < len(_chunks_metadata):
                chunk = _chunks_metadata[int(idx)]
                results.append({
                    "chunk_id": chunk.get("chunk_id"),
                    "source": chunk.get("source"),
                    "heading": chunk.get("heading"),
                    "text": chunk.get("text"),
                    "similarity_score": float(distances[i]),  # L2 distance (lower = more similar)
                })

        return results

    except Exception as e:
        print(f"[ERROR] RAG retrieval failed: {e}", file=sys.stderr)
        return []


def format_context(retrieved_chunks: List[Dict]) -> str:
    """
    Format retrieved chunks as a readable context section for the prompt.

    Args:
        retrieved_chunks: List of dicts returned by retrieve()

    Returns:
        Formatted context string ready to be prepended to the prompt
    """
    if not retrieved_chunks:
        return ""

    lines = ["KNOWLEDGE BASE CONTEXT (retrieved from HBNC clinical protocols):"]
    lines.append("")

    for chunk in retrieved_chunks:
        source = chunk.get("source", "unknown")
        heading = chunk.get("heading", "")
        text = chunk.get("text", "")

        if heading:
            lines.append(f"[{source} > {heading}]")
        else:
            lines.append(f"[{source}]")
        lines.append(text)
        lines.append("")

    lines.append("-" * 70)
    lines.append("")
    return "\n".join(lines)
