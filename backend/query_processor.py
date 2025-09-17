from gemini_llm_service import GeminiLLMService
from logger import logger
import os
from prompts.query_prompts import QUERY_GENERATION_PROMPT, DUMMY_QUERY
import json
from dotenv import load_dotenv
from faiss_indexer import FAISSIndexer
from repo_data_loader import RepoDataLoader
from pprint import pprint
load_dotenv()

filename = os.path.basename(__file__)

class QueryProcessor:
    """
    Handles multi-round query processing using Gemini LLM.
    """

    def __init__(self, repo_name: str, repo_structure_path: str, repo_readme_path: str, repo_metadata_path: str, repo_embeddings_path: str, repo_faiss_index_path: str, repo_chunks_path: str):
        self.gemini_service = GeminiLLMService()
        self.round1_queries_count = 6

        # Initialize RepoDataLoader
        loader = RepoDataLoader(
            repo_name=repo_name,
            repo_structure_path=repo_structure_path,
            repo_readme_path=repo_readme_path,
            repo_metadata_path=repo_metadata_path,
            repo_embeddings_path=repo_embeddings_path,
            repo_faiss_index_path=repo_faiss_index_path,
            repo_chunks_path=repo_chunks_path
        )

        # Load all repository data
        repo_data = loader.load_all()
        self.repo_structure = repo_data["repo_structure"]
        self.repo_readme = repo_data["repo_readme"]
        self.repo_metadata = repo_data["repo_metadata"]
        self.repo_embeddings = repo_data["repo_embeddings"]
        # self.repo_vector_store = repo_data["repo_faiss_index"]
        self.indexer = FAISSIndexer(embedding_file=repo_embeddings_path, repo_name=repo_name)
        self.repo_vector_store = self.indexer.load_index(repo_faiss_index_path)
        self.repo_chunks = repo_data["repo_chunks"]

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
        response = self.gemini_service.get_response(prompt, temperature=0.2)
        # logger.info(f"[{filename}] response - {response}.")

        # Parse the response into a JSON array of queries
        try:
            query_variants = json.loads(response)  # Assuming the response is a JSON array
            if isinstance(query_variants, list) and len(query_variants) == self.round1_queries_count:
                # Add the original query to the list of query variants
                query_variants.insert(0, user_query)
                logger.info(f"[{filename}] Generated {len(query_variants)} query variants including the original query.")
                return query_variants
            else:
                raise ValueError("Response does not contain the expected number of queries.")
        except Exception as e:
            logger.error(f"[{filename}] Error parsing query variants: {e}")
            return []

    def _retrieve_results(self, query_variants: list) -> dict:
        """
        Helper function to retrieve results for each query variant using FAISS indexer.

        Args:
            query_variants (list): List of query variants.

        Returns:
            dict: Retrieved results for each query.
        """
        retrieved_results = {}

        for query in query_variants:
            try:
                results = self.indexer.search(query, k=3)  # Default to top 3 results
                retrieved_results[query] = results
                logger.info(f"[{filename}] Retrieved {len(results)} results for query: {query}")
            except Exception as e:
                logger.error(f"[{filename}] Error retrieving results for query '{query}': {e}")

        return retrieved_results

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
        logger.info(f"[{filename}] Starting first round of query processing.")
        query_variants = self.process_first_round(user_query, repo_readme, repo_structure)
        logger.info(f"[{filename}] First round completed with {len(query_variants)} query variants.")

        # Retrieve results for each generated query

        logger.info(f"[{filename}] Retrieving results for generated query variants.")
        retrieved_results = self._retrieve_results(query_variants)
        logger.info(f"[{filename}] Retrieved results for all query variants.")

        return retrieved_results

# Additional helper functions or methods can be added here for subsequent rounds of processing.

if __name__ == "__main__":
    import argparse

    # Set up argument Parser
    parser = argparse.ArgumentParser(description="Test the process_first_round method.")
    parser.add_argument("--user_query", type=str, required=True, help="The user's original query.")
    parser.add_argument("--repo_name", type=str, required=True, help="Name of the repository.")
    parser.add_argument("--repo_structure_path", type=str, required=True, help="Path to the repository structure JSON file.")
    parser.add_argument("--repo_readme_path", type=str, required=True, help="Path to the repository README file.")
    parser.add_argument("--repo_metadata_path", type=str, required=True, help="Path to the repository metadata JSON file.")
    parser.add_argument("--repo_embeddings_path", type=str, required=True, help="Path to the repository embeddings file.")
    parser.add_argument("--repo_faiss_index_path", type=str, required=True, help="Path to the repository FAISS index file.")
    parser.add_argument("--repo_chunks_path", type=str, required=True, help="Path to the repository chunks file.")


    args = parser.parse_args()

    # Initialize QueryProcessor
    query_processor = QueryProcessor(
        repo_name=args.repo_name,
        repo_structure_path=args.repo_structure_path,
        repo_readme_path=args.repo_readme_path,
        repo_metadata_path=args.repo_metadata_path,
        repo_embeddings_path=args.repo_embeddings_path,
        repo_faiss_index_path=args.repo_faiss_index_path,
        repo_chunks_path=args.repo_chunks_path

    )

    # Call process_first_round
    query_variants = query_processor.process_first_round(
        user_query=args.user_query,
        repo_readme=query_processor.repo_readme,
        repo_structure=query_processor.repo_structure
    )

    # Call process_query
    retrieved_results = query_processor.process_query(
        user_query=args.user_query,
        repo_readme=query_processor.repo_readme,
        repo_structure=query_processor.repo_structure
    )

    # Print the results
    print("\nGenerated Query Variants:")
    for i, query in enumerate(query_variants, start=1):
        print(f"{i}: {query}")

    print("\nRetrieved Results:")
    for query, results in retrieved_results.items():
        print(f"Query: {query}")
        for doc, score in results:
            print(f"score {score} ")
            pprint(f"Document: {doc.page_content}")
            print("-----------------------------------------------------------------------------------")
            print("----------------------------------------------------------------------------------")
            