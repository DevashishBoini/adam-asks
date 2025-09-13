"""
Embedding Generator for Chunks
Phase 1, Step: Embedding Generation
File: backend/chunk_embedding_generator.py

Reads the chunk file, generates embeddings for each chunk's text using OpenAI embedding API,
and saves the results to a new file.
"""
import os
import json


from typing import List, Dict, Optional
from dataclasses import dataclass
from openai_embedder import get_openai_embedding
from logger import logger

filename = os.path.basename(__file__)

@dataclass
class Chunk:
    content: str
    metadata: Dict

class ChunkEmbeddingGenerator:
    def __init__(self, chunk_file_path: str, repo_name: str, output_dir: str = "repo_embeddings_dir", output_file: Optional[str] = None):
        self.chunk_file_path = chunk_file_path
        self.repo_name = repo_name
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        if output_file is None:
            self.output_file = os.path.join(self.output_dir, f"{self.repo_name}_embeddings.json")
        else:
            self.output_file = str(output_file)
        self.chunks = self._load_chunks()
        self.embeddings = []

    def _load_chunks(self) -> List[Chunk]:
        with open(self.chunk_file_path, "r") as f:
            raw_chunks = json.load(f)
        chunks = []
        for chunk in raw_chunks:
            metadata = {
                "file_path": chunk.get("file_path"),
                "start_line": chunk.get("start_line"),
                "end_line": chunk.get("end_line"),
                "symbols": chunk.get("symbols", [])
            }
            chunks.append(Chunk(
                content=chunk.get("text", ""),
                metadata=metadata
            ))
        return chunks


    def generate_embeddings(self, batch_size: int = 100):
        batch_chunks: List[Chunk] = []
        batch_no = 1
        total_chunks = len(self.chunks)
        for chunk in self.chunks:
            batch_chunks.append(chunk)
            if len(batch_chunks) == batch_size:
                self._process_batch(batch_chunks, batch_no)
                batch_chunks = []
                batch_no += 1
        if batch_chunks:
            self._process_batch(batch_chunks, batch_no)
        self._save_embeddings()
        # Count passed and failed
        passed = sum(1 for emb in self.embeddings if emb["embedding"] is not None)
        failed = total_chunks - passed
        logger.info(f"[{filename}] Total chunks arrived: {total_chunks}, passed: {passed}, failed: {failed}")

    def _process_batch(self, batch_chunks: List[Chunk], batch_no: int):
        texts = [chunk.content for chunk in batch_chunks]
        embeddings = self._get_batch_embeddings(texts, batch_no=batch_no)
        logger.info(f"[[{filename}] OpenAI embedding API call successful for batch #{batch_no} of {len(texts)} chunks.")
        for chunk, embedding in zip(batch_chunks, embeddings):
            chunk_embedding = {
                "content": chunk.content,
                "metadata": chunk.metadata,
                "embedding": embedding
            }
            self.embeddings.append(chunk_embedding)

    def _get_batch_embeddings(self, texts, batch_no=None):

        batch_info = f"batch #{batch_no}" if batch_no is not None else "batch"
        try:
            logger.info(f"[{filename}] Attempting batch embedding for {len(texts)} texts in {batch_info}.")
            result = get_openai_embedding(texts)
            logger.info(f"[{filename}] Batch embedding succeeded for {len(texts)} texts in {batch_info}.")
            return result
        except Exception as e:
            total_chars = sum(len(t) for t in texts)
            logger.error(f"[{filename}] Batch embedding failed for {len(texts)} texts in {batch_info}. Error: {e}. Total chars in batch: {total_chars}")
            # Recursive fallback: split batch and retry
            if len(texts) > 1:
                mid = len(texts) // 2
                left = texts[:mid]
                right = texts[mid:]
                logger.info(f"[{filename}] Splitting batch of {len(texts)} into two sub-batches: {len(left)} and {len(right)}.")
                try:
                    left_embeddings = self._get_batch_embeddings(left, batch_no=batch_no)
                    logger.info(f"[{filename}] Sub-batch embedding succeeded for left sub-batch of {len(left)} texts in {batch_info}.")
                except Exception as left_e:
                    logger.error(f"[{filename}] Sub-batch embedding failed for left sub-batch of {len(left)} texts in {batch_info}. Error: {left_e}")
                    left_embeddings = [None] * len(left)
                try:
                    right_embeddings = self._get_batch_embeddings(right, batch_no=batch_no)
                    logger.info(f"[{filename}] Sub-batch embedding succeeded for right sub-batch of {len(right)} texts in {batch_info}.")
                except Exception as right_e:
                    logger.error(f"[{filename}] Sub-batch embedding failed for right sub-batch of {len(right)} texts in {batch_info}. Error: {right_e}")
                    right_embeddings = [None] * len(right)
                return left_embeddings + right_embeddings
            else:
                # Fallback: process single
                embeddings = []
                for idx, text in enumerate(texts):
                    try:
                        logger.info(f"[{filename}] Attempting single embedding for text #{idx+1} in {batch_info}.")
                        embedding = get_openai_embedding(text)
                        logger.info(f"[{filename}] Single embedding succeeded for text #{idx+1} in {batch_info}.")
                        embeddings.append(embedding)
                    except Exception as single_e:
                        logger.error(f"[{filename}] Single embedding failed for text #{idx+1} in {batch_info}. Error: {single_e} . Total chars in batch: {total_chars}")
                        embeddings.append(None)
                return embeddings

    def _save_embeddings(self):
        with open(self.output_file, "w") as f:
            json.dump(self.embeddings, f, indent=4)
        logger.info(f"Embeddings saved to {self.output_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate embeddings for chunk texts using OpenAI API.")
    parser.add_argument("chunk_file_path", type=str, help="Path to the chunk file.")
    parser.add_argument("repo_name", type=str, help="Name of the repository.")
    parser.add_argument("--output_dir", type=str, default="repo_embeddings_dir", help="Directory to save the embeddings file.")
    parser.add_argument("--output_file", type=str, default=None, help="Path to save the embeddings file.")
    args = parser.parse_args()

    generator = ChunkEmbeddingGenerator(
        args.chunk_file_path,
        args.repo_name,
        args.output_dir,
        args.output_file
    )
    generator.generate_embeddings()
