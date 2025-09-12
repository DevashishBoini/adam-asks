#!/bin/bash

# Directory to store Tree-sitter grammars
grammar_dir="./tree-sitter-languages"

# Create the directory if it doesn't exist
mkdir -p "$grammar_dir"

# List of Tree-sitter grammar repositories to clone
declare -A grammars=(
  ["tree-sitter-python"]="https://github.com/tree-sitter/tree-sitter-python.git"
  ["tree-sitter-javascript"]="https://github.com/tree-sitter/tree-sitter-javascript.git"
  ["tree-sitter-typescript"]="https://github.com/tree-sitter/tree-sitter-typescript.git"
  ["tree-sitter-java"]="https://github.com/tree-sitter/tree-sitter-java.git"
  ["tree-sitter-c"]="https://github.com/tree-sitter/tree-sitter-c.git"
  ["tree-sitter-cpp"]="https://github.com/tree-sitter/tree-sitter-cpp.git"
  ["tree-sitter-go"]="https://github.com/tree-sitter/tree-sitter-go.git"
  ["tree-sitter-ruby"]="https://github.com/tree-sitter/tree-sitter-ruby.git"
)

# Clone each grammar repository
for grammar in "${!grammars[@]}"; do
  repo_url="${grammars[$grammar]}"
  target_dir="$grammar_dir/$grammar"

  if [ -d "$target_dir" ]; then
    echo "$grammar already exists in $target_dir. Skipping..."
  else
    echo "Cloning $grammar into $target_dir..."
    git clone "$repo_url" "$target_dir"
  fi
done

echo "All Tree-sitter grammars have been cloned into $grammar_dir."