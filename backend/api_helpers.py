"""
API Helpers - Phase 1, Step 1
Contains all business logic for FastAPI endpoints and common utilities.
"""
from typing import Dict, Any
from fastapi import HTTPException

from repository_service import RepositoryService, RepositoryError
from api_models import RepositoryInfo

class APIHelpers:
    """Contains helper functions for all API endpoints."""
    
    def __init__(self):
        self.repo_service = RepositoryService()
    
    @staticmethod
    def handle_repository_error(e: RepositoryError) -> HTTPException:
        """
        Convert RepositoryError to appropriate HTTPException.
        Reusable error handler for all endpoints dealing with repositories.
        
        Args:
            e: RepositoryError exception
            
        Returns:
            HTTPException with appropriate status code and error details
        """
        error_msg = str(e)
        
        # Map specific errors to HTTP status codes
        if "not found" in error_msg.lower() or "private" in error_msg.lower():
            error_code = "REPOSITORY_NOT_FOUND"
            status_code = 404
        elif "invalid" in error_msg.lower():
            error_code = "INVALID_URL"
            status_code = 400
        elif "timeout" in error_msg.lower():
            error_code = "TIMEOUT"
            status_code = 408
        elif "network" in error_msg.lower():
            error_code = "NETWORK_ERROR"
            status_code = 503
        else:
            error_code = "REPOSITORY_ERROR"
            status_code = 400
            
        return HTTPException(
            status_code=status_code,
            detail={
                "status": "error",
                "error_code": error_code,
                "message": error_msg
            }
        )
    
    @staticmethod
    def handle_unexpected_error(e: Exception) -> HTTPException:
        """
        Convert unexpected Exception to HTTPException.
        Reusable error handler for all endpoints.
        
        Args:
            e: Any unexpected exception
            
        Returns:
            HTTPException with 500 status code
        """
        return HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "INTERNAL_ERROR",
                "message": f"Unexpected error: {str(e)}"
            }
        )
    
    async def index_repository_helper(self, repo_url: str) -> Dict[str, Any]:
        """
        Business logic for repository indexing endpoint.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dictionary containing repository information and status
            
        Raises:
            RepositoryError: For repository-related errors
        """
        # Download repository
        result = await self.repo_service.download_repository(repo_url)
        
        # Create repository info
        repo_info = RepositoryInfo(
            owner=result["owner"],
            repo=result["repo"],
            local_path=result["local_path"],
            total_files=result["total_files"],
            status=result["status"]
        )
        
        # TODO: Phase 1, Step 2 - Add AST extraction here
        # TODO: Phase 1, Step 3 - Add metadata collection here
        # TODO: Phase 1, Step 4 - Add embedding generation here
        # TODO: Phase 1, Step 5 - Add FAISS storage here
        
        return {
            "status": "success",
            "message": f"Repository {result['owner']}/{result['repo']} downloaded successfully",
            "repo_info": repo_info
        }
    
    # TODO: Add more helper functions for future endpoints
    # async def search_code_helper(self, query: str) -> Dict[str, Any]:
    #     """Helper for code search endpoint."""
    #     pass
    
    # async def explain_code_helper(self, snippet_id: str) -> Dict[str, Any]:
    #     """Helper for code explanation endpoint."""
    #     pass
    
    def cleanup_repository(self, local_path: str) -> bool:
        """
        Clean up downloaded repository.
        
        Args:
            local_path: Path to the downloaded repository
            
        Returns:
            True if cleanup successful, False otherwise
        """
        return self.repo_service.cleanup_repository(local_path)