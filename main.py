"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
import os
import logging
from api.endpoints import bible_character, bible_verse, feeling
from core.dependencies import get_api_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Bible API",
    description="API for Bible verse explanations, character interactions, and feeling-based devotionals",
    version="1.0.0",
    dependencies=[Depends(get_api_key())]  # Add API key validation to all endpoints
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],  # Expose rate limit headers
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Import and include routers
# from controllers.bible_controller import router as bible_router
# app.include_router(bible_router, prefix="/api/v1")

# Include routers
app.include_router(bible_character.router)
app.include_router(bible_verse.router)
app.include_router(feeling.router, prefix="/api/v1", tags=["feelings"])

@app.get("/")
async def root():
    return {"message": "Welcome to Bible API"}

@app.get("/test")
async def test():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 