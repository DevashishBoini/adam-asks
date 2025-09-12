import argparse
from tree_sitter_languages import get_language
from tree_sitter import Parser
from pathlib import Path
from typing import List, Dict
import os
import json

# Ensure the script uses pre-built shared libraries for Tree-sitter languages.
LANGUAGES = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "java": "java",
    "c": "c",
    "cpp": "cpp",
    "go": "go",
    "ruby": "ruby"
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
    parser.set_language(get_language(language))

    with open(file_path, 'r') as f:
        code = f.read()

    tree = parser.parse(bytes(code, "utf8"))
    root_node = tree.root_node

    metadata = []

    def extract_nodes(node):
        # # Debug: print all attributes of the node
        # print(json.dumps({
        #     'type': node.type,
        #     'text': node.text.decode('utf8') if hasattr(node, 'text') else None,
        #     'start_point': node.start_point if hasattr(node, 'start_point') else None,
        #     'end_point': node.end_point if hasattr(node, 'end_point') else None,
        #     'child_count': node.child_count if hasattr(node, 'child_count') else None,
        #     'children_types': [child.type for child in node.children] if hasattr(node, 'children') else None,
        #     'fields': [str(node.child_by_field_name(f)) for f in ['name', 'body', 'parameters', 'decorator']] if hasattr(node, 'child_by_field_name') else None
        # }, indent=2, ensure_ascii=False))


        if node.type == "class_definition":
            entity = {
                "name": node.child_by_field_name("name").text.decode("utf8"),
                "type": "class",
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "docstring": None,
                "decorators": [],
                "methods": []
            }

            # Extract decorators (robust for Python Tree-sitter grammar)
            parent = node.parent
            if parent:
                idx = None
                for i, child in enumerate(parent.children):
                    if child == node:
                        idx = i
                        break
                if idx is not None:
                    i = idx - 1
                    while i >= 0 and parent.children[i].type == "decorator":
                        dec_node = parent.children[i]
                        dec_text = dec_node.text.decode("utf8").strip()
                        entity["decorators"].insert(0, dec_text)
                        i -= 1

            # Docstring extraction
            block = node.child_by_field_name("body")
            if block:
                for child in block.children:
                    # Docstring as expression_statement > string
                    if child.type == "expression_statement" and child.child_count > 0:
                        expr_child = child.children[0]
                        if expr_child.type == "string":
                            entity["docstring"] = expr_child.text.decode("utf8").strip('"\'')
                            break
                    if child.type == "string":
                        entity["docstring"] = child.text.decode("utf8").strip('"\'')
                        break

            # Extract methods (function_definition nodes inside class body)
            if block:
                for child in block.children:
                    if child.type == "function_definition":
                        # Recursively extract function metadata, but don't recurse further for nested classes
                        method_entity = {
                            "name": child.child_by_field_name("name").text.decode("utf8"),
                            "type": "function",
                            "start_line": child.start_point[0] + 1,
                            "end_line": child.end_point[0] + 1,
                            "docstring": None,
                            "decorators": []
                        }
                        # Decorators for method
                        method_parent = child.parent
                        if method_parent:
                            midx = None
                            for mi, mchild in enumerate(method_parent.children):
                                if mchild == child:
                                    midx = mi
                                    break
                            if midx is not None:
                                mi = midx - 1
                                while mi >= 0 and method_parent.children[mi].type == "decorator":
                                    mdec_node = method_parent.children[mi]
                                    mdec_text = mdec_node.text.decode("utf8").strip()
                                    method_entity["decorators"].insert(0, mdec_text)
                                    mi -= 1
                        # Docstring for method
                        mblock = child.child_by_field_name("body")
                        if mblock:
                            for mchild in mblock.children:
                                if mchild.type == "expression_statement" and mchild.child_count > 0:
                                    mexpr_child = mchild.children[0]
                                    if mexpr_child.type == "string":
                                        method_entity["docstring"] = mexpr_child.text.decode("utf8").strip('"\'')
                                        break
                                if mchild.type == "string":
                                    method_entity["docstring"] = mchild.text.decode("utf8").strip('"\'')
                                    break
                        entity["methods"].append(method_entity)

            metadata.append(entity)

        elif node.type == "function_definition":
            entity = {
                "name": node.child_by_field_name("name").text.decode("utf8"),
                "type": "function",
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "docstring": None,
                "decorators": []
            }

            # Extract decorators (robust for Python Tree-sitter grammar)
            parent = node.parent
            if parent:
                idx = None
                for i, child in enumerate(parent.children):
                    if child == node:
                        idx = i
                        break
                if idx is not None:
                    i = idx - 1
                    while i >= 0 and parent.children[i].type == "decorator":
                        dec_node = parent.children[i]
                        dec_text = dec_node.text.decode("utf8").strip()
                        entity["decorators"].insert(0, dec_text)
                        i -= 1

            # Docstring extraction
            block = node.child_by_field_name("body")
            if block:
                for child in block.children:
                    if child.type == "expression_statement" and child.child_count > 0:
                        expr_child = child.children[0]
                        if expr_child.type == "string":
                            entity["docstring"] = expr_child.text.decode("utf8").strip('"\'')
                            break
                    if child.type == "string":
                        entity["docstring"] = child.text.decode("utf8").strip('"\'')
                        break

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
        # # Pretty-print docstrings for each entity
        # for entity in metadata:
        #     if entity.get("docstring"):
        #         print(f"\nDocstring for {entity['type']} '{entity['name']}':\n" + entity["docstring"])

        # Custom pretty-print for docstring in JSON
        def docstring_to_lines(md):
            def convert_docstring(d):
                if isinstance(d, dict) and "docstring" in d and d["docstring"]:
                    # Convert docstring to list of lines
                    d["docstring"] = [line.strip() for line in d["docstring"].strip().splitlines()]
                return d
            return [convert_docstring(e.copy()) for e in md]

        print(json.dumps(docstring_to_lines(metadata), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")