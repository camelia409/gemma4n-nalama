#!/usr/bin/env python3
"""
HBNC Knowledge Base Builder
Reads raw markdown documents, chunks them intelligently, embeds them with Google's
embedding API, and saves a FAISS vector store for RAG retrieval.

Usage:
    python build-index.py --dry-run          # Preview chunks without embedding
    python build-index.py                    # Build the vector store (requires API key)

Environment:
    GOOGLE_API_KEY: Your Google AI Studio API key
"""

import os
import json
import argparse
import time
import re
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np

# Load .env file - try multiple locations
env_paths = [
    Path(__file__).parent / ".env",  # Script directory
    Path("knowledge_base/.env"),      # knowledge_base subdir
    Path(".env"),                      # Current directory
    Path("..")  / "knowledge_base" / ".env",  # Parent/knowledge_base
]

for env_path in env_paths:
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            break
        except Exception:
            pass

# Try to import libraries
try:
    import google.generativeai as genai
    import faiss
except ImportError as e:
    print(f"Error: Required library not installed. Please run:")
    print("pip install faiss-cpu google-generativeai numpy")
    exit(1)


class HBNCKnowledgeBaseBuilder:
    """Builder for HBNC knowledge base with intelligent chunking and embedding."""

    def __init__(self, api_key: str, dry_run: bool = False):
        """
        Initialize the builder.

        Args:
            api_key: Google API key
            dry_run: If True, don't call embedding API
        """
        self.api_key = api_key
        self.dry_run = dry_run
        self.raw_dir = Path("knowledge_base/raw")
        self.output_dir = Path("knowledge_base/embeddings")
        self.chunks: List[Dict] = []
        self.embeddings: List[List[float]] = []

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configure API
        if not dry_run:
            genai.configure(api_key=api_key)

    def read_raw_files(self) -> Dict[str, str]:
        """Read all markdown files from raw directory."""
        files = {}
        if not self.raw_dir.exists():
            raise FileNotFoundError(f"Directory not found: {self.raw_dir}")

        md_files = sorted(self.raw_dir.glob("*.md"))
        if not md_files:
            raise FileNotFoundError(f"No .md files found in {self.raw_dir}")

        print(f"\n[READ] Reading raw documents from {self.raw_dir}")
        for md_file in md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            files[md_file.name] = content
            print(f"   [OK] {md_file.name} ({len(content)} chars)")

        return files

    def split_by_headers(self, text: str) -> List[Tuple[str, str]]:
        """
        Split text by markdown ## headers.
        Returns list of (heading, section_text) tuples.
        """
        # Split by ## headers
        parts = re.split(r'^## ', text, flags=re.MULTILINE)

        sections = []
        for i, part in enumerate(parts):
            if i == 0 and not part.startswith('##'):
                # This is the intro before first header
                if part.strip():
                    sections.append(("INTRODUCTION", part))
            else:
                # Extract heading (first line) and content (rest)
                lines = part.split('\n', 1)
                if len(lines) == 2:
                    heading = lines[0].strip()
                    content = lines[1]
                    sections.append((heading, content))
                elif len(lines) == 1 and lines[0].strip():
                    sections.append((lines[0].strip(), ""))

        return sections

    def split_section_by_length(self, text: str, max_length: int = 500) -> List[str]:
        """
        Split a section into chunks if it exceeds max_length.
        Splits on paragraph boundaries to preserve context.
        """
        if len(text) <= max_length:
            return [text.strip()]

        # Split on double newlines (paragraphs)
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_length = len(para)

            # If single paragraph exceeds max_length, split it further
            if para_length > max_length:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_length = 0

                # Split long paragraph on sentences
                sentences = re.split(r'(?<=[.!?])\s+', para)
                sent_chunk = []
                sent_length = 0

                for sentence in sentences:
                    sent_len = len(sentence)
                    if sent_length + sent_len > max_length:
                        if sent_chunk:
                            chunks.append(' '.join(sent_chunk))
                            sent_chunk = []
                            sent_length = 0
                    sent_chunk.append(sentence)
                    sent_length += sent_len + 1

                if sent_chunk:
                    chunks.append(' '.join(sent_chunk))
            else:
                # Try to fit paragraph in current chunk
                if current_length + para_length + 2 > max_length and current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [para]
                    current_length = para_length
                else:
                    current_chunk.append(para)
                    current_length += para_length + 2

        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return [c.strip() for c in chunks if c.strip()]

    def chunk_documents(self, files: Dict[str, str]) -> None:
        """
        Chunk all documents intelligently.
        Store: source filename, heading, chunk text, chunk_id.
        """
        print(f"\n[CHUNK] Chunking documents (max 500 chars per chunk)")
        chunk_id = 0

        for filename in sorted(files.keys()):
            content = files[filename]
            sections = self.split_by_headers(content)

            for heading, section_text in sections:
                # Skip empty sections
                if not section_text.strip():
                    continue

                # Split section by length
                sub_chunks = self.split_section_by_length(section_text, max_length=500)

                for i, chunk_text in enumerate(sub_chunks):
                    if chunk_text.strip():
                        chunk_dict = {
                            "chunk_id": chunk_id,
                            "source": filename,
                            "heading": heading,
                            "chunk_index": i,
                            "text": chunk_text.strip(),
                            "length": len(chunk_text)
                        }
                        self.chunks.append(chunk_dict)
                        chunk_id += 1

        print(f"   [OK] Created {len(self.chunks)} chunks from {len(files)} files")

    def show_sample_chunks(self, num_samples: int = 3) -> None:
        """Display sample chunks for inspection."""
        print(f"\n[SAMPLES] Chunks (showing first {num_samples}):\n")

        for i, chunk in enumerate(self.chunks[:num_samples]):
            print(f"Chunk #{chunk['chunk_id']}")
            print(f"  Source: {chunk['source']}")
            print(f"  Heading: {chunk['heading']}")
            print(f"  Length: {chunk['length']} chars")
            print(f"  Text: {chunk['text'][:150]}...")
            print()

    def embed_chunks(self) -> None:
        """Embed all chunks using Google's embedding API."""
        if self.dry_run:
            print(f"\n[DRY-RUN] Skipping embeddings (would embed {len(self.chunks)} chunks)")
            return

        print(f"\n[EMBED] Embedding {len(self.chunks)} chunks with Google API")
        print(f"   Using: models/gemini-embedding-001 with RETRIEVAL_DOCUMENT task type")

        # Batch chunks while respecting free-tier rate limits (100 requests/min)
        # Use larger batches with long delays between them to stay under quota
        # Spreading batches across multiple minute windows
        batch_size = 50
        total_batches = (len(self.chunks) + batch_size - 1) // batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(self.chunks))
            batch = self.chunks[start_idx:end_idx]

            texts = [chunk["text"] for chunk in batch]

            # Retry logic for quota exceeded errors
            max_retries = 3
            retry_count = 0
            batch_embedded = False

            while retry_count < max_retries and not batch_embedded:
                try:
                    # Embed using Google's API
                    response = genai.embed_content(
                        model="models/gemini-embedding-001",
                        content=texts,
                        task_type="RETRIEVAL_DOCUMENT"
                    )

                    batch_embeddings = response["embedding"]
                    self.embeddings.extend(batch_embeddings)

                    print(f"   [OK] Batch {batch_num + 1}/{total_batches} ({len(texts)} chunks) - {len(self.embeddings)} total embedded")
                    batch_embedded = True

                    # Rate limiting: Very long delay to ensure batches don't hit quota limits
                    # Space batches far enough apart to stay under free-tier quota
                    if batch_num < total_batches - 1:
                        delay = 20.0  # 20 seconds between batches
                        print(f"       Waiting {delay:.1f}s before next batch...")
                        time.sleep(delay)

                except Exception as e:
                    error_str = str(e)
                    # Check if it's a quota/rate limit error
                    if "429" in error_str or "quota" in error_str.lower() or "resource_exhausted" in error_str.lower():
                        retry_count += 1
                        if retry_count < max_retries:
                            wait_time = 60 + (retry_count * 30)  # 60s, then 90s, then 120s
                            print(f"   [QUOTA] Batch {batch_num + 1} hit rate limit. Retry {retry_count}/{max_retries} in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            print(f"   [ERROR] Max retries exceeded for batch {batch_num + 1}")
                            raise
                    else:
                        print(f"   [ERROR] Error embedding batch {batch_num + 1}: {e}")
                        raise

        print(f"   [OK] Embedded {len(self.embeddings)} chunks successfully")

    def save_vector_store(self) -> None:
        """Save FAISS index and chunk metadata."""
        if self.dry_run:
            print(f"\n[DRY-RUN] Would save to {self.output_dir}")
            return

        print(f"\n[SAVE] Saving vector store to {self.output_dir}")

        # Convert embeddings to numpy array
        embeddings_array = np.array(self.embeddings).astype('float32')
        embedding_dim = embeddings_array.shape[1]

        print(f"   Embedding dimension: {embedding_dim}")
        print(f"   Total vectors: {len(self.embeddings)}")

        # Create FAISS index
        index = faiss.IndexFlatL2(embedding_dim)
        index.add(embeddings_array)

        # Save FAISS index
        index_path = self.output_dir / "faiss_index.bin"
        faiss.write_index(index, str(index_path))
        print(f"   [OK] Saved FAISS index: {index_path} ({index_path.stat().st_size / 1024:.1f} KB)")

        # Save metadata
        metadata = {
            "total_chunks": len(self.chunks),
            "embedding_model": "models/gemini-embedding-001",
            "embedding_dimension": embedding_dim,
            "chunks": self.chunks
        }

        metadata_path = self.output_dir / "chunks_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"   [OK] Saved metadata: {metadata_path} ({metadata_path.stat().st_size / 1024:.1f} KB)")

        print(f"\n[SUCCESS] Knowledge base built successfully!")
        print(f"   Vector store ready for RAG retrieval")

    def build(self) -> None:
        """Run the complete build process."""
        try:
            # Step 1: Read files
            files = self.read_raw_files()

            # Step 2: Chunk documents
            self.chunk_documents(files)

            # Step 3: Show samples
            self.show_sample_chunks()

            # Step 4: Embed (or skip if dry-run)
            self.embed_chunks()

            # Step 5: Save (or skip if dry-run)
            self.save_vector_store()

        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build HBNC knowledge base vector store"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview chunks without calling embedding API"
    )

    args = parser.parse_args()

    # Get API key from environment (only required if not dry-run)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key and not args.dry_run:
        print("[ERROR] GOOGLE_API_KEY environment variable not set")
        print("[INFO] Set it with: export GOOGLE_API_KEY='your-key'")
        exit(1)

    # For dry-run, use placeholder API key
    if not api_key:
        api_key = "placeholder-for-dry-run"

    # Build the knowledge base
    builder = HBNCKnowledgeBaseBuilder(api_key=api_key, dry_run=args.dry_run)
    builder.build()


if __name__ == "__main__":
    main()
