"""
FastAPI endpoints for Bible Character functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from typing import List
from services.bible_character import BibleCharacterService
from dtos.bible_character import (
    ChatRequestDTO,
    ChatResponseDTO
)
from core.dependencies import get_llm_client

router = APIRouter(
    prefix="/bible/characters",
    tags=["bible-characters"],
    responses={
        404: {"description": "Not found"}
    },
)

async def get_bible_character_service() -> BibleCharacterService:
    """Get or create BibleCharacterService instance."""
    service = BibleCharacterService(get_llm_client())
    await service.initialize()
    return service

@router.post("/chat", response_model=ChatResponseDTO)
async def chat_with_character(
    request: Request,
    response: Response,
    chat_request: ChatRequestDTO,
    service: BibleCharacterService = Depends(get_bible_character_service)
) -> ChatResponseDTO:
    """
    Chat with a biblical character.
    
    Args:
        request (Request): FastAPI request object
        response (Response): FastAPI response object
        chat_request (ChatRequestDTO): The chat request containing user message and context
        
    Returns:
        ChatResponseDTO: The character's response and conversation history
    """
    try:
        return await service.chat_with_character(chat_request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error chatting with character: {str(e)}"
        ) 