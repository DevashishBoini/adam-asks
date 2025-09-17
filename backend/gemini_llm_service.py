"""
Gemini LLM Service
Phase 1, Step: Query Optimization and Code Explanation
File: backend/gemini_llm_service.py

Provides a class to interact with Google's Gemini API for query rewriting, multi-query generation,
and code explanation. Uses Gemini 2.5 Flash model.
"""

import os
import google.generativeai as genai
from logger import logger
from dotenv import load_dotenv
import time

load_dotenv()

filename = os.path.basename(__file__)

class GeminiLLMService:
    """
    Service class for interacting with Google's Gemini API.
    Handles configuration, query rewriting, multi-query generation, and code explanation.
    """

    def __init__(self):
        """
        Initialize the Gemini LLM service.
        
        Args:
            api_key (Optional[str]): Google API key. If None, loads from environment.
            model_name (Optional[str]): Model name. Defaults to GEMINI_MODEL env var or 'gemini-2.0-flash-exp'.
        """
        if not os.getenv("GEMINI_API_KEY"):
                raise ValueError("GEMINI_API_KEY is not set in the environment.")
        
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model_flash = os.getenv("GEMINI_LLM_MODEL_FLASH", "gemini-2.5-flash")
        self.gemini_model_pro = os.getenv("GEMINI_LLM_MODEL_PRO", "gemini-2.5-pro")

        # Configure the API
        genai.configure(api_key=self.gemini_api_key)

        logger.info(f"[{filename}] GeminiLLMService initialized with model: {self.gemini_model_flash}")


    def get_response(self, query: str, temperature: float = 0.7, final_model: bool = False) -> str:
        """
        Generate a response from the Gemini model for a given query
        .
        
        Args:
            query
             (str): The input query
            .
            
        Returns:
            str: The generated response.
        """
        try:
            model_name = self.gemini_model_pro if final_model else self.gemini_model_flash
            logger.info(f"[{filename}] Using model: {model_name} with temperature: {temperature}")

            model = genai.GenerativeModel(model_name, generation_config={"temperature": temperature, "response_mime_type": "application/json"})

            # Start timer
            start_time = time.time()

            response = model.generate_content(query)

            # End timer and log time taken
            time_taken = time.time() - start_time
            logger.info(f"[{filename}] Time taken for API call: {time_taken:.2f} seconds")

            logger.info(f"[{filename}] Gemini API call successful for model: {model_name}")
            return response.text
        except Exception as e:
            logger.error(f"[{filename}] Gemini API error: {e}")
            raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test Gemini LLM service.")
    parser.add_argument("query", type=str, help="Query to process.")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for response generation.")
    parser.add_argument("--final_model", action="store_true", help="Use final model if available.")
    args = parser.parse_args()
    
    try:
        service = GeminiLLMService()
        
        # Test basic response
        response = service.get_response(args.query)
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
