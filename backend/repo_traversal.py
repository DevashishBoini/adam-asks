import os
from pathlib import Path
from typing import List, Tuple
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
    ".gemspec": "Ruby",
    ".md": "Markdown",
    ".rst": "reStructuredText",
    ".txt": "Text",
}

def traverse_repo(repo_path: str) -> Tuple[List[str], dict]:
    """
    Walk through all files in a repository and filter by supported language extensions.
    Additionally, generate the repository structure as a dictionary.

    Args:
        repo_path (str): Path to the repository.

    Returns:
        List[str]: List of file paths with supported extensions.
        dict: Repository structure as a nested dictionary.
    """
    if not os.path.isdir(repo_path):
        raise ValueError(f"The provided path '{repo_path}' is not a valid directory.")

    supported_files = []
    repo_structure = {}

    for root, _, files in os.walk(repo_path):
        # Generate the relative path from the root directory
        relative_path = os.path.relpath(root, repo_path)
        if relative_path == ".":
            current_level = repo_structure
        else:
            # Navigate to the correct level in the dictionary
            current_level = repo_structure
            for part in relative_path.split(os.sep):
                current_level = current_level.setdefault(part, {})

        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in SUPPORTED_EXTENSIONS:
                supported_files.append(str(file_path))

    return supported_files, repo_structure

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
        files, structure = traverse_repo(args.repo_path)
        print_files_with_language(files)
    except ValueError as e:
        print(e)