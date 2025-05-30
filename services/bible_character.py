"""
Service layer for Bible Character functionality.
"""

from typing import List, Optional
from datetime import datetime
from agents.bible_character import BibleCharacter
from dtos.bible_character import (
    CharacterContextDTO,
    MessageDTO,
    ChatRequestDTO,
    ChatResponseDTO
)

class BibleCharacterService:
    """Service for handling Bible Character interactions."""

    def __init__(self, llm_client):
        """
        Initialize the Bible Character service.
        
        Args:
            llm_client: The LLM client instance for making API calls
        """
        self.agent = BibleCharacter(llm_client)

    async def initialize(self):
        """Initialize the agent by starting the cleanup task."""
        await self.agent.start()

    async def cleanup(self):
        """Cleanup the agent by stopping the cleanup task."""
        await self.agent.stop()

    async def chat_with_character(self, request: ChatRequestDTO) -> ChatResponseDTO:
        """
        Handle chat interaction with a biblical character.
        
        Args:
            request (ChatRequestDTO): The chat request containing user message and context
            
        Returns:
            ChatResponseDTO: The character's response and conversation history
        """
        # Get character response
        response = await self.agent.chat_with_character(
            user_id=request.user_id,
            character_name=request.character_name,
            message=request.message
        )

        # Get conversation memory
        memory = self.agent.get_or_create_memory(
            user_id=request.user_id,
            character_name=request.character_name
        )

        # Get character context for display
        context = await self.agent.get_character_context(request.character_name)
        
        # Create brief character info for display
        character_info = {
            "Época": context.biographical_info.get("Época y lugar", ""),
            "Ocupación": context.biographical_info.get("Ocupación principal", ""),
            "Rasgos": context.character_traits.get("Rasgos principales", ""),
            "Legado": context.legacy.get("Importancia bíblica", "")
        }

        # Convert memory messages to DTOs
        conversation_history = [
            MessageDTO(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"]
            )
            for msg in memory.messages
        ]

        return ChatResponseDTO(
            character_name=request.character_name,
            response=response,
            conversation_history=conversation_history,
            character_info=character_info
        )

    async def get_character_context(self, character_name: str) -> CharacterContextDTO:
        """
        Get context information for a biblical character.
        
        Args:
            character_name (str): Name of the biblical character
            
        Returns:
            CharacterContextDTO: The character's context information
        """
        context = await self.agent.get_character_context(character_name)
        
        return CharacterContextDTO(
            name=context.name,
            biographical_info=context.biographical_info,
            key_events=context.key_events,
            character_traits=context.character_traits,
            legacy=context.legacy,
            bible_verses=context.bible_verses,
            extracted_at=context.extracted_at
        ) 