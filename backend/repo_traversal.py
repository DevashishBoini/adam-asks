import os
from pathlib import Path
from typing import List
import argparse

# Supported language extensions and their language names
SUPPORTED_EXTENSIONS = {
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".hpp": "C++",
    ".java": "Java",
    ".py": "Python",
    ".pyi": "Python",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rb": "Ruby",
    ".gemspec": "Ruby"
}

def traverse_repo(repo_path: str) -> List[str]:
    """
    Walk through all files in a repository and filter by supported language extensions.

    Args:
        repo_path (str): Path to the repository.

    Returns:
        List[str]: List of file paths with supported extensions.
    """
    if not os.path.isdir(repo_path):
        raise ValueError(f"The provided path '{repo_path}' is not a valid directory.")

    supported_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in SUPPORTED_EXTENSIONS:
                supported_files.append(str(file_path))

    return supported_files

def print_files_with_language(files: List[str]):
    """
    Print each file name with its corresponding programming language.

    Args:
        files (List[str]): List of file paths.
    """
    for file in files:
        file_extension = Path(file).suffix
        language = SUPPORTED_EXTENSIONS.get(file_extension, "Unknown")
        print(f"{file} -> [{language}]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traverse a repository and list supported files.")
    parser.add_argument("repo_path", type=str, help="Path to the repository to traverse.")
    args = parser.parse_args()

    try:
        files = traverse_repo(args.repo_path)
        print_files_with_language(files)
    except ValueError as e:
        print(e)