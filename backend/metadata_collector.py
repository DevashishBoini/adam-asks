import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from repo_traversal import traverse_repo
from ast_extractor import ASTExtractor
import concurrent.futures
import time
from logger import logger
import re
filename = os.path.basename(__file__)

class MetadataCollector:
    """
    Collects and stores metadata for a repository. Stores the path to the saved metadata file as an attribute.
    """
    def __init__(self, repo_path: str, repo_name: str, metadata_output_dir: str = "repo_metadatas_dir", readme_output_dir: str = "repo_readmes_dir", directory_structure_output_dir: str = "repo_structures_dir"):
        self.repo_path = repo_path
        self.repo_name = repo_name
        self.metadata_output_dir = metadata_output_dir
        self.readme_output_dir = readme_output_dir
        self.directory_structure_output_dir = directory_structure_output_dir
        self.metadata_path = None

    def process_file(self, file_path: str) -> Optional[Dict]:
        file_extension = Path(file_path).suffix
        if file_extension == ".py":
            language = "python"
            try:
                extractor = ASTExtractor(file_path, language)
                return extractor.extract()
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        return None

    def extract_readme_content(self, file_path: str) -> Optional[str]:
        """
        Extracts content from a README file.

        Args:
            file_path (str): Path to the README file.

        Returns:
            Optional[str]: The content of the README file with its path appended, or None if an error occurs.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # Only include non-empty files
                    return f"file path-{file_path}\ncontent-{content}"
        except Exception as e:
            logger.warning(f"[{filename}] Failed to read README file {file_path}: {e}")
        return None

    def collect_metadata_sequential(self) -> Dict[str, Any]:
        """
        Collects AST metadata for code files and README contents for documentation files
        in a single traversal loop of the repository.
        
        README files are identified using regex: case-insensitive 'readme' optionally
        followed by .md, .txt, or .rst.
        
        Returns:
            A dictionary with:
            - 'metadata': List of AST metadata dictionaries for code files.
            - 'readme_content': Concatenated string of README contents with delimiters.
        """
        metadata = []
        readme_contents = []
        readme_pattern = re.compile(r'(?i)readme(\.md|\.txt|\.rst)?$')
        
        files, repo_structure = traverse_repo(self.repo_path)
        for file_path in files:
            file_name = os.path.basename(file_path)
            if readme_pattern.match(file_name):
                # Collect README content
                readme_content = self.extract_readme_content(file_path)
                if readme_content:
                    readme_contents.append(readme_content)
            else:
                # Collect AST metadata for code files
                result = self.process_file(file_path)
                if result:
                    metadata.append(result)
        
        readme_content = "\n==============\n".join(readme_contents) if readme_contents else ""
        return {
            'metadata': metadata,
            'readme_content': readme_content,
            'repo_structure': repo_structure 
        }




    def save_metadata(self, metadata: List[Dict]):
        os.makedirs(self.metadata_output_dir, exist_ok=True)
        output_file = os.path.join(self.metadata_output_dir, f"{self.repo_name}_metadata.json")
        with open(output_file, "w") as f:
            json.dump(metadata, f, indent=4)
        self.metadata_path = output_file
        logger.info(f"[{filename}] Metadata collected and saved to {output_file}")
        return output_file

    def save_readme_content(self, readme_content: str):
        """
        Saves the README content to a file in the output directory.

        Args:
            readme_content (str): The concatenated README content to save.

        Returns:
            str: The path to the saved README content file.
        """
        os.makedirs(self.readme_output_dir, exist_ok=True)
        output_file = os.path.join(self.readme_output_dir, f"{self.repo_name}_readme_content.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(readme_content)
        logger.info(f"[{filename}] README content saved to {output_file}")
        return output_file

    def save_repo_structure(self, repo_structure: dict):
        """
        Saves the repository structure to a file in the output directory.

        Args:
            repo_structure (dict): The repository structure as a nested dictionary.

        Returns:
            str: The path to the saved repository structure file.
        """
        os.makedirs(self.directory_structure_output_dir, exist_ok=True)
        output_file = os.path.join(self.directory_structure_output_dir, f"{self.repo_name}_repo_structure.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(repo_structure, f, indent=4)
        logger.info(f"[{filename}] Repository structure saved to {output_file}")
        return output_file

    def run(self):
        start_time = time.time()
        response = self.collect_metadata_sequential()
        elapsed = time.time() - start_time
        logger.info(f"Sequential processing time: {elapsed:.2f} seconds")
        self.save_metadata(response['metadata'])
        self.save_readme_content(response['readme_content'])  # Save README content to file
        self.save_repo_structure(response['repo_structure'])  # Save repository structure to file


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Collect AST metadata for all supported files in a repository.")
    parser.add_argument("repo_path", type=str, help="Path to the repository to analyze.")
    parser.add_argument("repo_name", type=str, help="Name of the repository.")
    args = parser.parse_args()

    collector = MetadataCollector(args.repo_path, args.repo_name)
    collector.run()
    # The path to the stored metadata file is now available as collector.metadata_path