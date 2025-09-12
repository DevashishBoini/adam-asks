import json
import os
from pathlib import Path
from typing import Dict, List
from repo_traversal import traverse_repo
from ast_extractor import ASTExtractor

# Mapping file extensions to languages
EXTENSION_TO_LANGUAGE = {
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".java": "java",
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rb": "ruby",
    ".gemspec": "ruby"
}

def collect_metadata(repo_path: str) -> List[Dict]:
    """
    Collect metadata for all supported files in a repository.

    Args:
        repo_path (str): Path to the repository.

    Returns:
        List[Dict]: List of metadata for all files in the repository.
    """
    metadata = []
    files = traverse_repo(repo_path)
    for file_path in files:
        file_extension = Path(file_path).suffix
        # Only process Python files
        if file_extension == ".py": ## IMPORTANT - restricting to python directories only for now
            language = "python"
            try:
                extractor = ASTExtractor(file_path, language)
                file_metadata = extractor.extract()
                metadata.append(file_metadata)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    return metadata

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Collect AST metadata for all supported files in a repository.")
    parser.add_argument("repo_path", type=str, help="Path to the repository to analyze.")
    args = parser.parse_args()

    metadata = collect_metadata(args.repo_path)

    repo_name = os.path.basename(os.path.abspath(args.repo_path))
    output_dir = "repo_metadatas_dir"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{repo_name}_metadata.json")
    with open(output_file, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"Metadata collected and saved to {output_file}")