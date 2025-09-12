import argparse
from tree_sitter import Language, Parser
from pathlib import Path
from typing import List, Dict
import os

os.environ["CFLAGS"] = "-std=c11"
# Build the Tree-sitter language library (if not already built)
Language.build_library(
    './build/my-languages.so',
    [
        './tree-sitter-languages/tree-sitter-python',
        './tree-sitter-languages/tree-sitter-javascript',
        './tree-sitter-languages/tree-sitter-typescript/typescript',  # Adjusted for TypeScript
        './tree-sitter-languages/tree-sitter-typescript/tsx',         # Adjusted for TSX
        './tree-sitter-languages/tree-sitter-java',
        './tree-sitter-languages/tree-sitter-c',
        './tree-sitter-languages/tree-sitter-cpp',
        './tree-sitter-languages/tree-sitter-go',
        './tree-sitter-languages/tree-sitter-ruby'
    ]
)

# Load the language library
LANGUAGES = {
    "python": Language('./build/my-languages.so', 'python'),
    "javascript": Language('./build/my-languages.so', 'javascript'),
    "typescript": Language('./build/my-languages.so', 'typescript'),
    "java": Language('./build/my-languages.so', 'java'),
    "c": Language('./build/my-languages.so', 'c'),
    "cpp": Language('./build/my-languages.so', 'cpp'),
    "go": Language('./build/my-languages.so', 'go'),
    "ruby": Language('./build/my-languages.so', 'ruby')
}

def extract_ast_metadata(file_path: str, language: str) -> List[Dict]:
    """
    Extract functions and classes from a file using Tree-sitter, including docstrings if available.

    Args:
        file_path (str): Path to the file.
        language (str): Programming language of the file.

    Returns:
        List[Dict]: List of metadata for functions and classes.
    """
    parser = Parser()
    if language not in LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")

    parser.set_language(LANGUAGES[language])

    with open(file_path, 'r') as f:
        code = f.read()

    tree = parser.parse(bytes(code, "utf8"))
    root_node = tree.root_node

    metadata = []

    def extract_nodes(node):
        if node.type in ["function_definition", "class_definition"]:
            entity = {
                "name": node.child_by_field_name("name").text.decode("utf8"),
                "type": node.type.replace("_definition", ""),
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "docstring": None
            }

            # Attempt to extract docstring if available
            docstring_node = node.next_named_sibling
            if docstring_node and docstring_node.type == "string":
                entity["docstring"] = docstring_node.text.decode("utf8").strip('"\'')

            metadata.append(entity)

        for child in node.children:
            extract_nodes(child)

    extract_nodes(root_node)
    return metadata

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract AST metadata from a file.")
    parser.add_argument("file_path", type=str, help="Path to the file to analyze.")
    parser.add_argument("language", type=str, help="Programming language of the file.")
    args = parser.parse_args()

    try:
        metadata = extract_ast_metadata(args.file_path, args.language)
        print(metadata)
    except Exception as e:
        print(f"Error: {e}")