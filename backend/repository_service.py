"""
Repository Service - Phase 1, Step 0
Handles GitHub repository downloading, validation, and error handling using GitHub API.
"""
import os
import re
import tempfile
import shutil
import zipfile
import httpx
from urllib.parse import urlparse
from typing import Dict, Any, Optional

class RepositoryError(Exception):
    """Custom exception for repository-related errors."""
    pass

class RepositoryService:
    """Service for handling GitHub repository operations."""
    
    def __init__(self):
        # Store repos in backend/cloned_repos directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        self.clone_base_dir = os.path.join(backend_dir, "cloned_repos")
        os.makedirs(self.clone_base_dir, exist_ok=True)
    
    def validate_github_url(self, repo_url: str) -> Dict[str, str]:
        """
        Validate GitHub URL format and extract owner/repo name.
        
        Args:
            repo_url: GitHub repository URL (various formats supported)
            
        Returns:
            Dict with 'owner' and 'repo' keys
            
        Raises:
            RepositoryError: If URL format is invalid
        """
        # Normalize URL - handle various formats
        url = repo_url.strip()
        
        # Add https if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove www. if present
        url = url.replace('://www.github.com', '://github.com')
        
        # Remove trailing slashes and .git
        url = url.rstrip('/').replace('.git', '')
        
        # Match GitHub URL pattern
        pattern = r'https://github\.com/([a-zA-Z0-9._-]+)/([a-zA-Z0-9._-]+)$'
        match = re.match(pattern, url)
        
        if not match:
            raise RepositoryError("Invalid GitHub URL format. Expected: github.com/owner/repo")
        
        owner, repo = match.groups()
        return {"owner": owner, "repo": repo}
    
    def generate_local_path(self, owner: str, repo: str) -> str:
        """Generate local path for cloned repository."""
        repo_dir = f"{owner}_{repo}"
        return os.path.join(self.clone_base_dir, repo_dir)
    
    async def download_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Download GitHub repository using GitHub Archive API and return metadata.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dict with repository metadata and local path
            
        Raises:
            RepositoryError: If download fails
        """
        # Validate URL format
        repo_info = self.validate_github_url(repo_url)
        
        # Generate local path
        local_path = self.generate_local_path(repo_info["owner"], repo_info["repo"])
        
        # Remove existing directory if present
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
        
        # GitHub Archive API URL
        api_url = f"https://api.github.com/repos/{repo_info['owner']}/{repo_info['repo']}/zipball"
        
        try:
            async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
                # Download repository as ZIP
                response = await client.get(api_url)
                
                if response.status_code == 404:
                    raise RepositoryError("Repository not found or is private")
                elif response.status_code == 403:
                    raise RepositoryError("Repository access forbidden (likely private)")
                elif response.status_code != 200:
                    raise RepositoryError(f"GitHub API error: {response.status_code}")
                
                # Save ZIP file temporarily
                zip_path = local_path + ".zip"
                with open(zip_path, "wb") as f:
                    f.write(response.content)
                
                # Extract ZIP file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(local_path + "_temp")
                
                # GitHub creates a nested folder, move contents up
                temp_dir = local_path + "_temp"
                extracted_dirs = os.listdir(temp_dir)
                if extracted_dirs:
                    nested_path = os.path.join(temp_dir, extracted_dirs[0])
                    shutil.move(nested_path, local_path)
                    shutil.rmtree(temp_dir)
                
                # Clean up ZIP file
                os.remove(zip_path)
                
                # Count files in repository
                file_count = self._count_files(local_path)
                
                return {
                    "owner": repo_info["owner"],
                    "repo": repo_info["repo"],
                    "local_path": local_path,
                    "total_files": file_count,
                    "status": "downloaded"
                }
                
        except httpx.TimeoutException:
            raise RepositoryError("Repository download timed out (5 minutes)")
        except httpx.RequestError as e:
            raise RepositoryError(f"Network error: {str(e)}")
        except zipfile.BadZipFile:
            raise RepositoryError("Downloaded file is not a valid ZIP archive")
        except Exception as e:
            # Clean up on error
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
            zip_path = local_path + ".zip"
            if os.path.exists(zip_path):
                os.remove(zip_path)
            temp_path = local_path + "_temp"
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
            raise RepositoryError(f"Unexpected error during download: {str(e)}")
    
    def _count_files(self, directory: str) -> int:
        """Count total files in directory."""
        count = 0
        for root, dirs, files in os.walk(directory):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            count += len(files)
        return count
    
    def cleanup_repository(self, local_path: str) -> bool:
        """
        Clean up cloned repository.
        
        Args:
            local_path: Path to cloned repository
            
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
            return True
        except Exception:
            return False