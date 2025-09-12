
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from repo_traversal import traverse_repo
from ast_extractor import ASTExtractor
import concurrent.futures
import time

class MetadataCollector:
    """
    Collects and stores metadata for a repository. Stores the path to the saved metadata file as an attribute.
    """
    def __init__(self, repo_path: str, output_dir: str = "repo_metadatas_dir"):
        self.repo_path = repo_path
        self.output_dir = output_dir
        self.metadata_path = None

    def process_file(self, file_path: str) -> Optional[Dict]:
        file_extension = Path(file_path).suffix
        if file_extension == ".py":
            language = "python"
            try:
                extractor = ASTExtractor(file_path, language)
                return extractor.extract()
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        return None

    def collect_metadata_sequential(self) -> List[Dict]:
        metadata = []
        files = traverse_repo(self.repo_path)
        for file_path in files:
            result = self.process_file(file_path)
            if result:
                metadata.append(result)
        return metadata

    def save_metadata(self, metadata: List[Dict]):
        os.makedirs(self.output_dir, exist_ok=True)
        repo_name = os.path.basename(os.path.normpath(self.repo_path))
        output_file = os.path.join(self.output_dir, f"{repo_name}_metadata.json")
        with open(output_file, "w") as f:
            json.dump(metadata, f, indent=4)
        self.metadata_path = output_file
        print(f"Metadata collected and saved to {output_file}")

    def run(self):
        start_time = time.time()
        metadata = self.collect_metadata_sequential()
        elapsed = time.time() - start_time
        print(f"Sequential processing time: {elapsed:.2f} seconds")
        self.save_metadata(metadata)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Collect AST metadata for all supported files in a repository.")
    parser.add_argument("repo_path", type=str, help="Path to the repository to analyze.")
    args = parser.parse_args()

    collector = MetadataCollector(args.repo_path)
    collector.run()
    # The path to the stored metadata file is now available as collector.metadata_path