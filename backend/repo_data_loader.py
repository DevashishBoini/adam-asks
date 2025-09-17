import json
import os
from logger import logger
from langchain_community.vectorstores import FAISS
from openai_embedder import get_openai_embedding

filename = os.path.basename(__file__)

class RepoDataLoader:
    """
    A class to load repository data including structure, README, and metadata.
    """

    def __init__(self, repo_name: str, repo_structure_path: str, repo_readme_path: str, repo_metadata_path: str, repo_embeddings_path: str, repo_faiss_index_path: str, repo_chunks_path: str, embedder=get_openai_embedding):
        self.repo_name = repo_name
        self.repo_structure_path = repo_structure_path
        self.repo_readme_path = repo_readme_path
        self.repo_metadata_path = repo_metadata_path
        self.repo_embeddings_path = repo_embeddings_path
        self.repo_faiss_index_path = repo_faiss_index_path
        self.repo_chunks_path = repo_chunks_path
        self.embedder = embedder

    def load_repo_structure(self) -> dict:
        """
        Load and truncate the repository structure.

        Returns:
            dict: Truncated repository structure.
        """
        try:
            with open(self.repo_structure_path, 'r', encoding='utf-8') as f:
                repo_structure = json.load(f)
            logger.info(f"[{filename}] Repository structure loaded successfully.")

            # Truncate repository structure to a depth of 3
            def truncate_structure(structure, depth):
                if depth == 0 or not isinstance(structure, dict):
                    return {}
                return {key: truncate_structure(value, depth - 1) for key, value in structure.items()}

            return truncate_structure(repo_structure, 3)
        except Exception as e:
            logger.error(f"[{filename}] Failed to load repository structure: {e}")
            return {}

    def load_repo_readme(self) -> str:
        """
        Load and truncate the repository README content.

        Returns:
            str: Truncated README content.
        """
        try:
            with open(self.repo_readme_path, 'r', encoding='utf-8') as f:
                repo_readme = f.read()

            # Truncate README content if it exceeds 1550 characters
            if len(repo_readme) > 1550:
                repo_readme = repo_readme[:1550] + "\n[README content truncated]"

            logger.info(f"[{filename}] Repository README content loaded successfully.")
            return repo_readme
        except Exception as e:
            logger.error(f"[{filename}] Failed to load repository README content: {e}")
            return ""

    def load_repo_metadata(self) -> dict:
        """
        Load the repository metadata.

        Returns:
            dict: Repository metadata.
        """
        try:
            with open(self.repo_metadata_path, 'r', encoding='utf-8') as f:
                repo_metadata = json.load(f)
            logger.info(f"[{filename}] Repository metadata loaded successfully.")
            return repo_metadata
        except Exception as e:
            logger.error(f"[{filename}] Failed to load repository metadata: {e}")
            return {}

    def load_repo_embeddings(self) -> dict:
        """
        Load the repository embeddings.

        Returns:
            dict: Repository embeddings.
        """
        try:
            with open(self.repo_embeddings_path, 'r', encoding='utf-8') as f:
                repo_embeddings = json.load(f)
            logger.info(f"[{filename}] Repository embeddings loaded successfully.")
            return repo_embeddings
        except Exception as e:
            logger.error(f"[{filename}] Failed to load repository embeddings: {e}")
            return {}

    # def load_repo_faiss_index(self):
    #     """
    #     Load the FAISS index data.

    #     Returns:
    #         FAISS: Loaded FAISS index.
    #     """
    #     try:
    #         logger.info(f"[RepoDataLoader] Loading FAISS index from {self.repo_faiss_index_path}.")
    #         faiss_index = FAISS.load_local(self.repo_faiss_index_path, self.embedder, allow_dangerous_deserialization=True)
    #         logger.info(f"[RepoDataLoader] FAISS index loaded successfully.")
    #         return faiss_index
    #     except Exception as e:
    #         logger.error(f"[RepoDataLoader] Failed to load FAISS index: {e}")
    #         return None

    def load_repo_chunks(self) -> dict:
        """
        Load the repository chunks data.

        Returns:
            dict: Repository chunks data.
        """
        try:
            with open(self.repo_chunks_path, 'r', encoding='utf-8') as f:
                repo_chunks = json.load(f)
            logger.info(f"[RepoDataLoader] Repository chunks loaded successfully.")
            return repo_chunks
        except Exception as e:
            logger.error(f"[RepoDataLoader] Failed to load repository chunks: {e}")
            return {}

    def load_all(self) -> dict:
        """
        Load all repository data.

        Returns:
            dict: A dictionary containing the repository structure, README content, metadata, embeddings, FAISS index, and chunks.
        """
        return {
            "repo_structure": self.load_repo_structure(),
            "repo_readme": self.load_repo_readme(),
            "repo_metadata": self.load_repo_metadata(),
            "repo_embeddings": self.load_repo_embeddings(),
            # "repo_faiss_index": self.load_repo_faiss_index(),
            "repo_chunks": self.load_repo_chunks()
        }