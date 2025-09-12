"""
Test script for Repository Service
Tests GitHub repository downloading, URL validation, and error handling.
"""
import asyncio
import os
import sys

# Add parent directory to path to import repository_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository_service import RepositoryService, RepositoryError

async def test_repository_service():
    """Test the RepositoryService functionality."""
    
    service = RepositoryService()
    
    print("=== Testing Repository Service ===\n")
    
    # Test 1: URL Validation
    print("1. Testing URL validation...")
    
    test_urls = [
        "https://github.com/octocat/Hello-World",  # Valid
        "github.com/octocat/Hello-World",          # Missing https
        "https://www.github.com/octocat/Hello-World/",  # With www and trailing slash
        "https://github.com/octocat/Hello-World.git",   # With .git
        "https://github.com/invalid-url",          # Invalid format
        "not-a-url",                               # Not a URL
    ]
    
    for url in test_urls:
        try:
            result = service.validate_github_url(url)
            print(f"✅ {url} -> {result['owner']}/{result['repo']}")
        except RepositoryError as e:
            print(f"❌ {url} -> {e}")
    
    print()
    
    # Test 2: Download a public repository
    print("2. Testing repository download...")
    
    test_repo = "https://github.com/octocat/Hello-World"  # Small public repo
    
    try:
        print(f"Downloading: {test_repo}")
        result = await service.download_repository(test_repo)
        
        print(f"✅ Download successful!")
        print(f"   Owner: {result['owner']}")
        print(f"   Repo: {result['repo']}")
        print(f"   Local path: {result['local_path']}")
        print(f"   Total files: {result['total_files']}")
        print(f"   Status: {result['status']}")
        
        # Verify files exist
        if os.path.exists(result['local_path']):
            files = os.listdir(result['local_path'])
            print(f"   Sample files: {files[:5]}")
        
        # Cleanup
        print("   Cleaning up...")
        cleanup_success = service.cleanup_repository(result['local_path'])
        print(f"   Cleanup: {'✅ Success' if cleanup_success else '❌ Failed'}")
        
    except RepositoryError as e:
        print(f"❌ Download failed: {e}")
    
    print()
    
    # Test 3: Test error cases
    print("3. Testing error cases...")
    
    error_test_cases = [
        ("https://github.com/nonexistent/repo-that-does-not-exist", "Non-existent repo"),
        ("https://github.com/microsoft/vscode", "Large private-like repo (might be rate limited)"),
    ]
    
    for url, description in error_test_cases:
        try:
            print(f"Testing: {description}")
            result = await service.download_repository(url)
            print(f"✅ Unexpected success: {result}")
        except RepositoryError as e:
            print(f"✅ Expected error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    asyncio.run(test_repository_service())