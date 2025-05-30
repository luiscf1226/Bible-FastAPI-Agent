"""
Core dependencies for the application.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import Request, Response, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from services.rate_limiter import rate_limiter
from datetime import datetime

# Load environment variables
load_dotenv()

# API Key header configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def get_api_key():
    """
    Validate the API key from the request header.
    
    Returns:
        str: The validated API key
        
    Raises:
        HTTPException: If the API key is invalid or missing
    """
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="API key not configured in environment variables"
        )
    
    async def validate_api_key(api_key_header: str = Security(api_key_header)):
        if api_key_header != api_key:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key"
            )
        return api_key_header
    
    return validate_api_key

def get_llm_client():
    """
    Get an instance of the LLM client.
    
    Returns:
        OpenAI: Configured OpenAI client
    """
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    )

def create_rate_limit_dependency(endpoint: str):
    """
    Create a rate limit dependency for a specific endpoint.
    
    Args:
        endpoint (str): The endpoint identifier (e.g., 'bible_verse_explain', 'bible_character_chat')
        
    Returns:
        callable: A dependency function that checks rate limits for the specific endpoint
    """
    async def check_rate_limit(request: Request, response: Response):
        """
        Dependency to check rate limits for a specific endpoint.
        Adds rate limit headers to the response.
        """
        client_ip = request.client.host
        
        # Check rate limit
        if rate_limiter.is_rate_limited(endpoint, client_ip):
            reset_time = rate_limiter.get_reset_time(endpoint, client_ip)
            remaining_time = reset_time - datetime.now()
            hours = int(remaining_time.total_seconds() // 3600)
            minutes = int((remaining_time.total_seconds() % 3600) // 60)
            
            raise HTTPException(
                status_code=429,
                detail={
                    "message": f"Rate limit exceeded for {endpoint}",
                    "remaining_time": f"{hours} hours and {minutes} minutes",
                    "reset_time": reset_time.isoformat(),
                    "limit": "5 requests per 24 hours"
                }
            )
        
        # Add rate limit information to response headers
        remaining_requests = rate_limiter.get_remaining_requests(endpoint, client_ip)
        reset_time = rate_limiter.get_reset_time(endpoint, client_ip)
        
        # Set rate limit headers
        response.headers["X-RateLimit-Limit"] = "5"
        response.headers["X-RateLimit-Remaining"] = str(remaining_requests)
        response.headers["X-RateLimit-Reset"] = reset_time.isoformat()
        response.headers["X-RateLimit-Endpoint"] = endpoint
    
    return check_rate_limit 