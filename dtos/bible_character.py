"""
Data Transfer Objects for Bible Character endpoints.
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CharacterContextDTO(BaseModel):
    """DTO for character context information."""
    name: str
    biographical_info: Dict[str, str]
    key_events: List[str]
    character_traits: Dict[str, str]
    legacy: Dict[str, str]
    bible_verses: List[str]
    extracted_at: datetime

class MessageDTO(BaseModel):
    """DTO for a single message in the conversation."""
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequestDTO(BaseModel):
    """DTO for chat request."""
    user_id: str = Field(..., description="Unique identifier for the user")
    character_name: str = Field(..., description="Name of the biblical character")
    message: str = Field(..., description="User's message to the character")

class ChatResponseDTO(BaseModel):
    """DTO for chat response."""
    character_name: str = Field(..., description="Name of the biblical character")
    response: str = Field(..., description="Character's response")
    conversation_history: List[MessageDTO] = Field(..., description="Recent conversation history")
    character_info: Dict[str, str] = Field(..., description="Brief character information for display") 