"""
Main FastAPI Application - Phase 1, Step 1
Repository indexing API with GitHub repository download functionality.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from repository_service import RepositoryError
from api_models import IndexRepositoryRequest, IndexRepositoryResponse, ErrorResponse
from api_helpers import APIHelpers
from logger import logger

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Mini GitHub Copilot API",
    description="Semantic code search and explanation API for GitHub repositories",
    version="0.1.0"
)

# Initialize API helpers
api_helpers = APIHelpers()
filename = os.path.basename(__file__)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Mini GitHub Copilot API is running"}

@app.get("/dummy")
async def dummy():
    """Dummy endpoint for testing (Phase 0)."""
    return {"message": "Hello from backend!"}

@app.post("/index-repo", 
          response_model=IndexRepositoryResponse,
          responses={
              400: {"model": ErrorResponse, "description": "Bad Request"},
              404: {"model": ErrorResponse, "description": "Repository Not Found"},
              500: {"model": ErrorResponse, "description": "Internal Server Error"}
          })
async def index_repository(request: IndexRepositoryRequest):
    """
    Download and index a GitHub repository.
    
    This endpoint:
    1. Validates the GitHub repository URL
    2. Downloads the repository using GitHub Archive API
    3. Prepares it for code extraction and indexing
    
    Args:
        request: Repository indexing request with GitHub URL
        
    Returns:
        Repository information and indexing status
        
    Raises:
        HTTPException: For various error conditions
    """
    logger.info(f"[{filename}] Received index-repo request for URL: {request.repo_url}")
    try:
        # Use API helpers to handle the business logic
        result = await api_helpers.index_repository_helper(request.repo_url)
        logger.info(f"[{filename}] Indexing successful for {request.repo_url}")
        return IndexRepositoryResponse(
            status=result["status"],
            message=result["message"],
            repo_info=result["repo_info"]
        )
    except RepositoryError as e:
        logger.error(f"[{filename}] RepositoryError for {request.repo_url}: {e}")
        raise api_helpers.handle_repository_error(e)
    except Exception as e:
        logger.error(f"[{filename}] Unexpected error for {request.repo_url}: {e}")
        raise api_helpers.handle_unexpected_error(e)

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    
    uvicorn.run(app, host=host, port=port)