"""
Phase 1, Step: Chunking Orchestration
File: backend/chunk_orchestrator.py

This module provides a ChunkOrchestrator class that traverses all files in a repo,
fetches metadata, creates chunks, and stores them for further processing.
"""

import os
import json
from typing import List, Dict, Any
from metadata_collector import MetadataCollector
from chunk_generator import ChunkGenerator
from logger import logger
filename = os.path.basename(__file__)

class ChunkOrchestrator:
    def __init__(self, repo_path: str, metadata_path: str, repo_name: str):
        self.chunks = []
        self.repo_path = repo_path
        self.metadata_path = metadata_path
        self.repo_name = repo_name
        self.file_metadatas = []
        self.chunk_file_path = None

    def collect_file_metadatas(self):
        """
        Load file metadata from the metadata_path (JSON file).
        """
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_path}")
        with open(self.metadata_path, "r") as f:
            self.file_metadatas = json.load(f)
        return self.file_metadatas

    def generate_all_chunks(self):
        # Traverse all files in the repo and generate chunks using corresponding metadata
        files = [os.path.join(root, file)
                 for root, _, files in os.walk(self.repo_path)
                 for file in files if file.endswith('.py')]
        # Build a mapping from file_path to metadata
        metadata_map = {meta.get('file_path'): meta for meta in self.file_metadatas}
        for file_path in files:
            file_metadata = metadata_map.get(file_path)
            if not file_metadata:
                continue
            entities = file_metadata.get('entities', [])
            chunk_gen = ChunkGenerator(file_path, entities)
            file_chunks = chunk_gen.generate_chunks()
            self.chunks.extend(file_chunks)
        logger.info(f"[{filename}] Total chunks generated: {len(self.chunks)}")
        return self.chunks

    def save_chunks(self, output_dir: str = "repo_chunks_dir"):
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{self.repo_name}_chunks.json")
        with open(output_file, "w") as f:
            json.dump(self.chunks, f, indent=4)
        logger.info(f"[{filename}] All chunks saved to {output_file}")
        self.chunk_file_path = output_file
        return output_file

    def run(self):
        self.collect_file_metadatas()
        self.generate_all_chunks()
        return self.save_chunks()
