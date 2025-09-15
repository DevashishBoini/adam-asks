"""
OpenAI Embedding Utility
Phase 1, Step: Embedding Generation
File: backend/openai_embedder.py

Provides a function to generate an embedding for a given text chunk using OpenAI API.
"""

import os
import requests
from dotenv import load_dotenv
from typing import Union, List

from logger import logger
filename = os.path.basename(__file__)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/embeddings")


def get_openai_embedding(text: Union[str, List[str]]):
    if not OPENAI_API_KEY:
        logger.error(f"[{filename}] OPENAI_API_KEY is not set in the environment.")
        raise ValueError("OPENAI_API_KEY is not set in the environment.")
    logger.info(f"[{filename}] Generating embedding using model: {OPENAI_EMBEDDING_MODEL}")
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "input": text,
        "model": OPENAI_EMBEDDING_MODEL
    }
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        # logger.error(f"[{filename}] OpenAI API HTTP error: {http_err}, Response: {response.text}")
        raise
    except Exception as e:
        logger.error(f"[{filename}] OpenAI API general error: {e}")
        raise
    resp_json = response.json()
    # If batch, return list of embeddings
    # logger.info(f"[{filename}] Input type: {type(text)}")
    if isinstance(text, list):
        logger.info(f"[{filename}] Batch embedding generation for {len(text)} texts ")
        embeddings = [item["embedding"] for item in resp_json["data"]]
        logger.info(f"[{filename}] Embedding dimension of 1st text in batch: {len(embeddings[0])}")
        return embeddings
    # If single string, return single embedding
    logger.info(f"[{filename}] Single embedding generation")
    return resp_json["data"][0]["embedding"]



if __name__ == "__main__":
    sample_text = "This is a test sentence for OpenAI embedding generation."
    try:
        embedding = get_openai_embedding(sample_text)
        if embedding is not None:
            print(f"Embedding generated for sample text: {embedding[:10]}... (truncated)")
            print(f"Embedding length: {len(embedding)}")
        else:
            print("No embedding returned.")
    except Exception as e:
        print(f"Error: {e}")