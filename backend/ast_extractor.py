from typing import Any
import argparse
from tree_sitter_languages import get_language
from tree_sitter import Parser
from pathlib import Path
from typing import List, Dict
import pprint
import os
import json
import re

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

# --- Helper functions for attribute extraction ---

# --- OOP Extractors ---
class FunctionExtractor:
    @staticmethod
    def get_visibility(name: str) -> str:
        if name.startswith("__") and not name.endswith("__"):
            return "private"
        elif name.startswith("_"):
            return "private"
        else:
            return "public"
    @staticmethod
    def extract_is_async(node: Any) -> bool:
        return node.type == "async_function_definition" or (
            node.type == "function_definition" and
            len(node.children) > 0 and node.children[0].type == "async"
        )

    @staticmethod
    def extract_return_type(node: Any) -> str:
        # Extracts the return type annotation if present
        type_node = node.child_by_field_name("return_type")
        if type_node:
            return type_node.text.decode("utf8").strip()
        return ""
    
    @staticmethod
    def extract_decorators(node: Any) -> list:
        decorators = []
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
                    decorators.insert(0, dec_text)
                    i -= 1
        return decorators

    @staticmethod
    def extract_docstring(node: Any) -> Any:
        block = node.child_by_field_name("body")
        if block:
            for child in block.children:
                if child.type == "expression_statement" and child.child_count > 0:
                    expr_child = child.children[0]
                    if expr_child.type == "string":
                        text=expr_child.text.decode("utf8").strip('"\'')
                        return re.sub(r"\s+", " ", text).strip()
                if child.type == "string":
                    text=child.text.decode("utf8").strip('"\'')
                    return re.sub(r"\s+", " ", text).strip()
        return None

    @staticmethod
    def extract_parameters(node: Any) -> list:
        params = []
        param_node = node.child_by_field_name("parameters")
        func_name = node.child_by_field_name("name")
        func_name = func_name.text.decode("utf8") if func_name else None

        if param_node:
            # print(f"\n[DEBUG] Function: {func_name}")
            # print("[DEBUG] Raw param_node info:")
            for i, child in enumerate(param_node.children):
                text = child.text.decode("utf8").strip()
                # print(f"  Param {i}: type={child.type}, text={text}")
                if text in ('(', ')', ',', ':', 'self', 'cls'):
                    continue
                param_info = {"type": child.type}

                if child.type == "identifier":
                    # if text == '(' or text == ')' or text == ',':
                    #     continue
                    # if func_name == "__init__" and text == "self":
                    #     param_info["kind"] = "instance"
                    param_info["name"] = text

                elif child.type == "typed_parameter":
                    name, _, type_ann = text.partition(":")
                    param_info["name"] = name.strip()
                    param_info["type_annotation"] = type_ann.strip() if type_ann else None

                elif child.type == "default_parameter":
                    name, _, default = text.partition("=")
                    param_info["name"] = name.strip()
                    param_info["default_value"] = default.strip() if default else None

                elif child.type == "typed_default_parameter":
                    name, _, rest = text.partition(":")
                    if "=" in rest:
                        type_ann, _, default = rest.partition("=")
                        param_info["type_annotation"] = type_ann.strip()
                        param_info["default_value"] = default.strip()
                    else:
                        param_info["type_annotation"] = rest.strip()
                    param_info["name"] = name.strip()

                elif child.type == "list_splat_pattern":
                    param_info["name"] = text.lstrip("*").strip()
                    param_info["kind"] = "*args"

                elif child.type == "dictionary_splat_pattern":
                    param_info["name"] = text.lstrip("**").strip()
                    param_info["kind"] = "**kwargs"

                if param_info: params.append(param_info)
        return params

    @staticmethod
    def extract_name(node: Any) -> str:
        name_node = node.child_by_field_name("name")
        if name_node:
            return name_node.text.decode("utf8")
        return ""

    @staticmethod
    def extract(node: Any) -> dict:
        name = FunctionExtractor.extract_name(node)
        return {
            "name": name,
            "type": "function",
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "docstring": FunctionExtractor.extract_docstring(node),
            "decorators": FunctionExtractor.extract_decorators(node),
            "parameters": FunctionExtractor.extract_parameters(node),
            "return_type_annotation": FunctionExtractor.extract_return_type(node),
            "is_async": FunctionExtractor.extract_is_async(node),
            "visibility": FunctionExtractor.get_visibility(name)
        }


    # @staticmethod
    # def extract_return_type(node: Any) -> str:
    #     # Extracts the return type annotation if present
    #     type_node = node.child_by_field_name("return_type")
    #     if type_node:
    #         return type_node.text.decode("utf8").strip()
    #     return ""
    #     if name_node:
    #         func_name = name_node.text.decode("utf8")

    #     if param_node:

    #         print(f"\n[DEBUG] Function: {func_name}")
    #         print("[DEBUG] Raw param_node info:")
    #         for i, child in enumerate(param_node.children):
    #             print(f"  Param {i}: type={child.type}, text={child.text.decode('utf8')}")

    #             param_info = {}
    #             # Handle regular, typed, default, and keyword-only parameters
    #             if child.type == "identifier" :
    #                 param_info["name"] = child.text.decode("utf8").strip()
    #                 param_info["type"]=child.type
                
    #             elif child.type == "typed_parameter" :
    #                 text=child.text.decode("utf8").strip()
    #                 param_info["name"]=text.split(":")[0].strip()
    #                 param_info["type_annotation"]=text.split(":")[1].strip() if ":" in text else None
    #                 param_info["type"]=child.type

    #             elif child.type == "default_parameter" :
    #                 text=child.text.decode("utf8").strip()
    #                 param_info["name"]=text.split("=")[0].strip()
    #                 param_info["default_value"]=text.split("=")[1].strip() if "=" in text else None
    #                 param_info["type"]=child.type

    #                 # print(f"default_parameter - {param_info["default_value"]} ")

    #             elif child.type == "typed_default_parameter" :
    #                 text=child.text.decode("utf8").strip()
    #                 param_info["name"]=text.split(":")[0].strip()
    #                 rest=text.split(":")[1].strip() if ":" in text else None
    #                 if rest and "=" in rest:
    #                     param_info["type_annotation"]=rest.split("=")[0].strip()
    #                     param_info["default_value"]=rest.split("=")[1].strip()
    #                 else:
    #                     param_info["type_annotation"]=rest
    #                 param_info["type"]=child.type
    #                 # print(f"typed_default_parameter - {param_info["default_value"]} ")
                
    #             elif child.type == "list_splat_pattern" :
    #                 text=child.text.decode("utf8").strip()
    #                 param_info["name"]=text.lstrip("*").strip()
    #                 param_info["kind"]="*args"
    #                 param_info["type"]=child.type

    #             elif child.type == "dictionary_splat_pattern" :
    #                 text=child.text.decode("utf8").strip()
    #                 param_info["name"]=text.lstrip("**").strip()
    #                 param_info["kind"]="**kwargs"
    #                 param_info["type"]=child.type


    #             if param_info: params.append(param_info)

    #             if child.type in ["identifier", "typed_parameter", "default_parameter", "typed_default_parameter"]:

    #                 # Name
    #                 name_node = child.child_by_field_name("name")
    #                 if name_node:
    #                     param_info["name"] = name_node.text.decode("utf8")
    #                     print(param_info["name"])
    #                 else :
    #                     text = child.text.decode("utf8").strip()
    #                     key = text.split(" : ")[0] if " : " in text else None
    #                 # Type annotation
    #                 type_node = child.child_by_field_name("type")
    #                 if type_node:
    #                     param_info["type_annotation"] = type_node.text.decode("utf8")
    #                 # Default value
    #                 default_node = child.child_by_field_name("default")
    #                 if default_node:
    #                     param_info["default_value"] = default_node.text.decode("utf8")
    #                 # Also check direct children for type/default
    #                 for c in child.children:
    #                     if c.type == "type":
    #                         param_info["type_annotation"] = c.text.decode("utf8")
    #                     if c.type == "default":
    #                         param_info["default_value"] = c.text.decode("utf8")
    #                 params.append(param_info)
    #             # *args
    #             elif child.type == "list_splat":
    #                 param_info["name"] = child.text.decode("utf8")
    #                 param_info["kind"] = "*args"
    #                 params.append(param_info)
    #             # **kwargs
    #             elif child.type == "dictionary_splat":
    #                 param_info["name"] = child.text.decode("utf8")
    #                 param_info["kind"] = "**kwargs"
    #                 params.append(param_info)
    #             # Keyword-only and splat parameters
    #             elif child.type in ["keyword_parameter", "keyword_splat_parameter"]:
    #                 param_info["name"] = child.text.decode("utf8")
    #                 param_info["kind"] = "keyword"
    #                 params.append(param_info)
    #     return params

    # @staticmethod
    # def extract(node: Any) -> dict:
    #     return {
    #         "name": node.child_by_field_name("name").text.decode("utf8"),
    #         "type": "function",
    #         "start_line": node.start_point[0] + 1,
    #         "end_line": node.end_point[0] + 1,
    #         "docstring": FunctionExtractor.extract_docstring(node),
    #         "decorators": FunctionExtractor.extract_decorators(node),
    #         "parameters": FunctionExtractor.extract_parameters(node)
    #     }

class ClassExtractor:
    @staticmethod
    def get_visibility(name: str) -> str:
        if name.startswith("__") and not name.endswith("__"):
            return "private"
        elif name.startswith("_"):
            return "private"
        else:
            return "public"
    @staticmethod
    def extract_base_classes(node: Any) -> list:
        # Extracts base class names if present
        bases = []
        base_node = node.child_by_field_name("superclasses")
        if base_node:
            for child in base_node.children:
                # Only extract identifiers and dotted names
                if child.type in ("identifier", "dotted_name"):
                    bases.append(child.text.decode("utf8").strip())
        return bases
    @staticmethod
    def extract_decorators(node: Any) -> list:
        return FunctionExtractor.extract_decorators(node)

    @staticmethod
    def extract_docstring(node: Any) -> Any:
        return FunctionExtractor.extract_docstring(node)

    @staticmethod
    def extract_methods(node: Any) -> list:
        methods = []
        block = node.child_by_field_name("body")
        if block:
            for child in block.children:
                if child.type == "function_definition":
                    method_metadata = {
                        "name": FunctionExtractor.extract_name(child),
                        "docstring": FunctionExtractor.extract_docstring(child)
                    }
                    methods.append(method_metadata)
        return methods

    @staticmethod
    def extract(node: Any) -> dict:
        name = node.child_by_field_name("name").text.decode("utf8")
        return {
            "name": name,
            "type": "class",
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "docstring": ClassExtractor.extract_docstring(node),
            "decorators": ClassExtractor.extract_decorators(node),
            "base_classes": ClassExtractor.extract_base_classes(node),
            "methods": ClassExtractor.extract_methods(node),
            "visibility": ClassExtractor.get_visibility(name)
        }


class ASTExtractor:

    def extract_imports(self) -> list:
        """Recursively extract all import statements from the AST."""
        imports = []
        def find_imports(node):
            if node.type in ("import_statement", "import_from_statement"):
                imports.append(node.text.decode("utf8").strip())
            for child in node.children:
                find_imports(child)
        find_imports(self.root_node)
        return imports

    def extract_file_docstring(self) -> Any:
        """Extract the top-level file/module docstring, if present."""
        # Look for a string node at the top of the file (PEP 257)
        for node in self.root_node.children:
            if node.type == "expression_statement" and node.child_count > 0:
                expr_child = node.children[0]
                if expr_child.type == "string":
                    return expr_child.text.decode("utf8").strip('"\'')
            if node.type == "string":
                return node.text.decode("utf8").strip('"\'')
        return None

        

    def __init__(self, file_path: str, language: str):
        self.file_path = file_path
        self.language = language
        self.parser = Parser()
        self.parser.set_language(get_language(language))
        with open(file_path, 'r') as f:
            self.code = f.read()
        self.tree = self.parser.parse(bytes(self.code, "utf8"))
        self.root_node = self.tree.root_node
        self.num_lines = len(self.code.splitlines())
        self.imports = self.extract_imports()
        self.file_docstring = self.extract_file_docstring()

    def extract(self) -> Dict:
        entities = []

        def extract_nodes(node):
            if node.type == "class_definition":
                entities.append(ClassExtractor.extract(node))
            elif node.type in ("function_definition", "async_function_definition"):
                entities.append(FunctionExtractor.extract(node))
            for child in node.children:
                extract_nodes(child)

        extract_nodes(self.root_node)

        # Sort entities by start_line before returning
        entities.sort(key=lambda entity: entity["start_line"])

        return {
            "file_path": self.file_path,
            "language": self.language,
            "num_lines": self.num_lines,
            "file_docstring": self.file_docstring,
            "imports": self.imports,
            "entities": entities
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract AST metadata from a file.")
    parser.add_argument("file_path", type=str, help="Path to the file to analyze.")
    parser.add_argument("language", type=str, help="Programming language of the file.")
    args = parser.parse_args()

    def format_docstrings(obj):
        """Recursively format all docstrings in metadata as lists of lines."""
        if isinstance(obj, dict):
            new_obj = obj.copy()
            if "docstring" in new_obj and new_obj["docstring"]:
                new_obj["docstring"] = [line.strip() for line in new_obj["docstring"].strip().splitlines()]
            for k, v in new_obj.items():
                new_obj[k] = format_docstrings(v)
            return new_obj
        elif isinstance(obj, list):
            return [format_docstrings(item) for item in obj]
        else:
            return obj

    try:
        extractor = ASTExtractor(args.file_path, args.language)
        metadata = extractor.extract()
        formatted_metadata = format_docstrings(metadata)
        pprint.pprint(formatted_metadata, indent=2, width=120, compact=False)
    except Exception as e:
        print(f"Error: {e}")