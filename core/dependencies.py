"""
Core dependencies for the application.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import Request, Response, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader

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