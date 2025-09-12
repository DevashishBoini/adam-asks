import json
from pathlib import Path
from typing import Dict, List
from repo_traversal import traverse_repo
from ast_extractor import extract_ast_metadata

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

    # Traverse the repository to get all supported files
    files = traverse_repo(repo_path)

    for file_path in files:
        file_extension = Path(file_path).suffix
        language = EXTENSION_TO_LANGUAGE.get(file_extension)

        if language:
            try:
                # Extract AST metadata for the file
                file_metadata = extract_ast_metadata(file_path, language)
                metadata.append({
                    "file_path": file_path,
                    "language": language,
                    "entities": file_metadata
                })
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    return metadata

if __name__ == "__main__":
    repo_path = "./cloned_repos"  # Example repository path
    metadata = collect_metadata(repo_path)

    # Save metadata to a JSON file
    output_file = "repo_metadata.json"
    with open(output_file, "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"Metadata collected and saved to {output_file}")