"""
API Models - Phase 1, Step 1
Pydantic models for repository indexing API requests and responses.
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any

class IndexRepositoryRequest(BaseModel):
    """Request model for repository indexing."""
    repo_url: str = Field(
        ...,
        description="GitHub repository URL (https://github.com/owner/repo)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "repo_url": "https://github.com/octocat/Hello-World"
            }
        }

class RepositoryInfo(BaseModel):
    """Repository information model."""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    local_path: str = Field(..., description="Local storage path")
    total_files: int = Field(..., description="Total number of files")
    status: str = Field(..., description="Processing status")

class IndexRepositoryResponse(BaseModel):
    """Response model for successful repository indexing."""
    status: str = Field("success", description="Operation status")
    message: str = Field(..., description="Success message")
    repo_info: RepositoryInfo = Field(..., description="Repository information")

class ErrorResponse(BaseModel):
    """Response model for errors."""
    status: str = Field("error", description="Operation status")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "error_code": "INVALID_URL",
                "message": "Invalid GitHub URL format"
            }
        }