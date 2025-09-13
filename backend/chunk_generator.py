"""
Phase 1, Step: Chunking
File: backend/chunk_generator.py

This module provides a ChunkGenerator class that creates function/class-level chunks from file metadata.
If no functions/classes are found, the whole file is treated as a single chunk.
Each chunk includes start/end line, file_path, and symbols (keywords for lexical matching).
"""

import re
from typing import List, Dict, Any
from pathlib import Path

class ChunkGenerator:
    def __init__(self, file_path: str, file_metadata: List[Dict]):
        self.file_path = file_path
        self.file_metadata = file_metadata
        self.chunks = []

    def extract_symbols(self, text: str) -> List[str]:
        # Extract keywords (identifiers, function/class names, etc.)
        # Simple regex for Python identifiers
        return list(set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', text)))

    def get_chunk_text(self, start: int, end: int) -> str:
        with open(self.file_path, 'r') as f:
            lines = f.readlines()
        return ''.join(lines[start-1:end])

    def generate_chunks(self) -> List[Dict[str, Any]]:
        if not self.file_metadata:
            # No functions/classes, treat whole file as one chunk
            with open(self.file_path, 'r') as f:
                text = f.read()
            symbols = self.extract_symbols(text)
            chunk = {
                'file_path': self.file_path,
                'start_line': 1,
                'end_line': len(text.splitlines()),
                'symbols': symbols,
                'text': text
            }
            self.chunks.append(chunk)
        else:
            for item in self.file_metadata:
                start = item.get('start_line', 1)
                end = item.get('end_line', 1)
                chunk_text = self.get_chunk_text(start, end)
                symbols = self.extract_symbols(chunk_text)
                chunk = {
                    'file_path': self.file_path,
                    'start_line': start,
                    'end_line': end,
                    'symbols': symbols,
                    'text': chunk_text
                }
                self.chunks.append(chunk)
        return self.chunks
