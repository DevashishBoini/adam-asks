import json
import os
import numpy as np
from langchain_community.vectorstores import FAISS
from openai_embedder import get_openai_embedding
import argparse
from logger import logger
from pprint import pprint

filename = os.path.basename(__file__)

class FAISSIndexer:
    def __init__(self, embedding_file: str, repo_name: str, embedder=get_openai_embedding, distance_strategy : str ="fssds"):
        """
        Initialize the FAISSIndexer.

        :param embedding_file: Path to the JSON file containing embeddings.
        :param embedder: Embedding function, defaults to OpenAI embedding function.
        :param distance_strategy: Distance strategy for FAISS (e.g., "cosine").
        """
        self.embedding_file = embedding_file
        self.embedder = embedder
        self.repo_name = repo_name
        self.distance_strategy = distance_strategy

    def load_data(self):
        """
        Load text, embeddings, and metadata from the specified JSON file.

        :return: Tuple of texts, embeddings, and metadata.
        """
        logger.info(f"[{__file__}] Loading data from embedding file: {self.embedding_file}")
        with open(self.embedding_file, "r") as f:
            data = json.load(f)
        texts = [item["content"] for item in data]
        embeddings = np.array([item["embedding"] for item in data])
        # no need of normalization here as FAISS handles it internally for cosine similarity and openAI also returns normalised vectors
        # embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)  

        metadatas = [item["metadata"] for item in data]
        logger.info(f"[{__file__}] Successfully loaded {len(texts)} texts, {len(embeddings)} embeddings, and {len(metadatas)} metadata entries.")
        return texts, embeddings, metadatas

    def create_index(self, texts, embeddings, metadatas):
        """
        Create a FAISS index from texts, embeddings, and metadata.

        :param texts: List of text chunks.
        :param embeddings: NumPy array of embeddings.
        :param metadatas: List of metadata dictionaries.
        """
        logger.info(f"[{filename}] Creating FAISS index with {len(texts)} entries.")
        self.vector_store = FAISS.from_embeddings(
            text_embeddings=list(zip(texts, embeddings)),
            embedding=self.embedder,
            metadatas=metadatas,
            # distance_strategy=self.distance_strategy
        )
        logger.info(f"[{filename}] FAISS index created successfully.")

    def add_to_index(self, texts, embeddings, metadatas):
        """
        Add new data to the existing FAISS index.

        :param texts: List of text chunks.
        :param embeddings: NumPy array of embeddings.
        :param metadatas: List of metadata dictionaries.
        """
        self.vector_store.add_embeddings(
            text_embeddings=list(zip(texts, embeddings)),
            metadatas=metadatas
        )

    def save_index(self, output_dir='repo_faiss_index_dir'):
        """
        Save the FAISS index to a file.

        :param output_dir: Directory to save the FAISS index file.
        """
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{self.repo_name}_index.json")
        logger.info(f"[{filename}] Saving FAISS index to {file_path}.")
        self.vector_store.save_local(file_path)
        logger.info(f"[{filename}] FAISS index saved successfully at {file_path}.")

        return file_path

    def load_index(self, file_path):
        """
        Load a FAISS index from a file.

        :param file_path: Path to the saved FAISS index.
        """
        logger.info(f"[{filename}] Loading FAISS index from {file_path}.")
        self.vector_store = FAISS.load_local(file_path, self.embedder, allow_dangerous_deserialization=True)
        logger.info(f"[{filename}] FAISS index loaded successfully at {file_path}.")
        return self.vector_store

    def search(self, query, k=5):
        """
        Perform a similarity search on the FAISS index.

        :param query: Query text for the search.
        :param k: Number of top results to return.
        :return: List of search results.
        """
        logger.info(f"[{filename}] Performing similarity search for query: {query} with top {k} results.")
        results = self.vector_store.similarity_search_with_score(query, k=k)
        # normalized_results = [(doc, score) for doc, score in results]
        normalized_results = []
        for doc, raw_score in results:
        # Convert L2 distance (FAISS default) -> cosine similarity
            cosine_sim = 1 - (raw_score ** 2) / 2
            # Map from [-1, 1] -> [0, 1] relevance score
            relevance = (cosine_sim + 1) / 2
            normalized_results.append((doc, relevance))

        sorted_results = sorted(normalized_results, key=lambda x: x[1], reverse=True)
        logger.info(f"[{filename}] Similarity search completed. Found {len(results)} results.")
        return sorted_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FAISS Indexer for text, embeddings, and metadata.")
    parser.add_argument("embedding_file", type=str, help="Path to the JSON file containing embeddings.")
    parser.add_argument("repo_name", type=str, help="Name of the repository.")
    parser.add_argument("query", type=str, help="Query text for similarity search.")
    args = parser.parse_args()

    indexer = FAISSIndexer(embedding_file=args.embedding_file, repo_name=args.repo_name)

    # Load data from the specified JSON file
    texts, embeddings, metadatas = indexer.load_data()

    # Create the FAISS index
    indexer.create_index(texts, embeddings, metadatas)

    # Save the FAISS index to disk
    file_path = indexer.save_index()

    # Load the index from disk
    indexer.load_index(file_path)

    # Perform a search with the provided query
    results = indexer.search(args.query, k=5)

    # Print embedding model from .env
    embedding_model_env = os.getenv("OPENAI_EMBEDDING_MODEL")
    print(f"[INFO] Embedding model from .env: {embedding_model_env}")

    # Print embedding model used in get_openai_embedding
    from openai_embedder import OPENAI_EMBEDDING_MODEL
    print(f"[INFO] Embedding model used in get_openai_embedding: {OPENAI_EMBEDDING_MODEL}")

    # Print dimensions of the model (from OpenAI docs or by generating a sample embedding)
    sample_text = "dimension check"
    sample_embedding = get_openai_embedding(sample_text)
    print(f"[INFO] Dimension of embedding from get_openai_embedding: {len(sample_embedding)}")

    # Print dimensions of the stored embeddings
    if len(embeddings) > 0:
        print(f"[INFO] Dimension of stored embeddings: {embeddings.shape[1]}")
    else:
        print("[INFO] No embeddings found in the file.")

    pprint("Search Results:")
    print()
    print(f'found {len(results)} results')
    for result, score in results:
        print(f"Score: {score}")
        pprint(result.page_content)
        print("-----------------------------------------------------------------------------------")
        print("----------------------------------------------------------------------------------")


