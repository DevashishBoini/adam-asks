from gemini_llm_service import GeminiLLMService
from logger import logger
import os
from prompts.query_prompts import QUERY_GENERATION_PROMPT, DUMMY_QUERY
import json
from dotenv import load_dotenv
load_dotenv()

filename = os.path.basename(__file__)

class QueryProcessor:
    """
    Handles multi-round query processing using Gemini LLM.
    """

    def __init__(self, repo_structure_path: str, repo_readme_path: str, repo_metadata_path: str):
        self.gemini_service = GeminiLLMService()
        self.round1_queries_count = 5

        # Load repository data using separate helper functions
        self.repo_structure = self._load_repo_structure(repo_structure_path)
        self.repo_readme = self._load_repo_readme(repo_readme_path)
        self.repo_metadata = self._load_repo_metadata(repo_metadata_path)

    def _load_repo_structure(self, repo_structure_path: str) -> dict:
        """
        Helper function to load and truncate the repository structure.

        Args:
            repo_structure_path (str): Path to the repository structure JSON file.

        Returns:
            dict: Truncated repository structure.
        """
        try:
            with open(repo_structure_path, 'r', encoding='utf-8') as f:
                repo_structure = json.load(f)
            logger.info(f"[{filename}] Repository structure loaded successfully.")

            # Truncate repository structure to a depth of 3
            def truncate_structure(structure, depth):
                if depth == 0 or not isinstance(structure, dict):
                    return {}
                return {key: truncate_structure(value, depth - 1) for key, value in structure.items()}

            truncated_structure = truncate_structure(repo_structure, 3)
            logger.info(f"[{filename}] Repository structure loaded successfully.")
            # logger.info(f"[{filename}] truncated repo structure - {truncated_structure}.")
            return truncated_structure
        except Exception as e:
            logger.error(f"[{filename}] Failed to load repository structure: {e}")
            return {}

    def _load_repo_readme(self, repo_readme_path: str) -> str:
        """
        Helper function to load and truncate the repository README content.

        Args:
            repo_readme_path (str): Path to the repository README file.

        Returns:
            str: Truncated README content.
        """
        try:
            with open(repo_readme_path, 'r', encoding='utf-8') as f:
                repo_readme = f.read()

            # Truncate README content if it exceeds 1550 characters
            if len(repo_readme) > 1550:
                repo_readme = repo_readme[:1550] + "\n[README content truncated]"

            logger.info(f"[{filename}] Repository README content loaded successfully.")
            # logger.info(f"[{filename}] repo_readme - {repo_readme}.")
            return repo_readme
        except Exception as e:
            logger.error(f"[{filename}] Failed to load repository README content: {e}")
            return ""

    def _load_repo_metadata(self, repo_metadata_path: str) -> dict:
        """
        Helper function to load the repository metadata.

        Args:
            repo_metadata_path (str): Path to the repository metadata JSON file.

        Returns:
            dict: Repository metadata.
        """
        try:
            with open(repo_metadata_path, 'r', encoding='utf-8') as f:
                repo_metadata = json.load(f)
            logger.info(f"[{filename}] Repository metadata loaded successfully.")
            return repo_metadata
        except Exception as e:
            logger.error(f"[{filename}] Failed to load repository metadata: {e}")
            return {}

    def process_first_round(self, user_query: str, repo_readme: str, repo_structure: dict) -> list:
        """
        Handles the first round of query processing by generating multiple query variants.

        Args:
            user_query (str): The user's original query.
            repo_readme (str): Content of the repository's README.
            repo_structure (dict): Structure of the repository as a dictionary.
            num_queries (int): Number of query variants to generate.

        Returns:
            list: A list of query variants.
        """
        # Format the prompt with placeholders
        prompt = QUERY_GENERATION_PROMPT.format(
            user_query=user_query,
            num_queries=self.round1_queries_count,
            repo_readme=repo_readme,
            repo_structure=repo_structure
        )
        # prompt = DUMMY_QUERY

        logger.info(f"[{filename}] Sending query generation prompt to Gemini LLM.")
        response = self.gemini_service.get_response(prompt)
        logger.info(f"[{filename}] response - {response}.")

        # Parse the response into a JSON array of queries
        try:
            query_variants = json.loads(response)  # Assuming the response is a JSON array
            if isinstance(query_variants, list) and len(query_variants) == self.round1_queries_count:
                logger.info(f"[{filename}] Generated {len(query_variants)} query variants.")
                return query_variants
            else:
                raise ValueError("Response does not contain the expected number of queries.")
        except Exception as e:
            logger.error(f"[{filename}] Error parsing query variants: {e}")
            return []

    def process_query(self, user_query: str, repo_readme: str, repo_structure: dict):
        """
        Orchestrates the multi-round query processing.

        Args:
            user_query (str): The user's original query.
            repo_readme (str): Content of the repository's README.
            repo_structure (dict): Structure of the repository as a dictionary.

        Returns:
            list: Final processed queries or results.
        """
        # First round: Generate query variants
        query_variants = self.process_first_round(user_query, repo_readme, repo_structure)

        # Placeholder for subsequent rounds
        # ...additional processing logic...

        return query_variants

# Additional helper functions or methods can be added here for subsequent rounds of processing.

if __name__ == "__main__":
    import argparse

    # Set up argument Parser
    parser = argparse.ArgumentParser(description="Test the process_first_round method.")
    parser.add_argument("--user_query", type=str, required=True, help="The user's original query.")
    parser.add_argument("--repo_structure_path", type=str, required=True, help="Path to the repository structure JSON file.")
    parser.add_argument("--repo_readme_path", type=str, required=True, help="Path to the repository README file.")
    parser.add_argument("--repo_metadata_path", type=str, required=True, help="Path to the repository metadata JSON file.")


    args = parser.parse_args()

    # Initialize QueryProcessor
    query_processor = QueryProcessor(
        repo_structure_path=args.repo_structure_path,
        repo_readme_path=args.repo_readme_path,
        repo_metadata_path=args.repo_metadata_path
    )

    # Call process_first_round
    query_variants = query_processor.process_first_round(
        user_query=args.user_query,
        repo_readme=query_processor.repo_readme,
        repo_structure=query_processor.repo_structure
    )

    # Print the results
    print("Generated Query Variants:")
    for i, query in enumerate(query_variants, start=1):
        print(f"{i}: {query}")