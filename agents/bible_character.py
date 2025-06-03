"""
Bible Character Agent Implementation

This module implements the BibleCharacter class that handles:
- Character context extraction and storage
- Conversation memory management
- LLM API interactions
- Response generation
- Session management with timeout
"""

from typing import Dict, Optional, List, Deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
import uuid
import asyncio
import logging
from .prompts.bible_character_agent import (
    get_character_prompt,
    get_response_prompt,
    get_system_prompt,
    CHARACTER_SYSTEM_PROMPT
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CharacterContext:
    """Stores extracted information about a biblical character."""
    name: str
    biographical_info: Dict[str, str]
    key_events: List[str]
    character_traits: Dict[str, str]
    legacy: Dict[str, str]
    bible_verses: List[str]
    extracted_at: datetime

    def to_dict(self) -> Dict:
        """Convert character context to a dictionary format."""
        return {
            "name": self.name,
            "biographical_info": self.biographical_info,
            "key_events": self.key_events,
            "character_traits": self.character_traits,
            "legacy": self.legacy,
            "bible_verses": self.bible_verses
        }

@dataclass
class UserSession:
    """Manages user session state and timeout."""
    user_id: str
    created_at: datetime
    last_activity: datetime
    is_active: bool = True

@dataclass
class ConversationMemory:
    """Stores conversation history for a user session with window-based memory."""
    user_id: str
    character_name: str
    messages: Deque[Dict[str, str]]
    created_at: datetime
    last_updated: datetime
    window_size: int = 8  # Number of exchanges to keep (16 total messages)

    def __post_init__(self):
        """Initialize the messages deque with the specified window size."""
        if not isinstance(self.messages, deque):
            self.messages = deque(maxlen=self.window_size * 2)  # *2 because each exchange has 2 messages

    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        })
        self.last_updated = datetime.utcnow()

    def get_formatted_history(self) -> str:
        """Format conversation history for the LLM prompt."""
        formatted_history = []
        for msg in self.messages:
            role = "Usuario" if msg["role"] == "user" else "Personaje"
            formatted_history.append(f"{role}: {msg['content']}")
        return "\n".join(formatted_history)

class BibleCharacter:
    def __init__(self, llm_client, session_timeout_minutes: int = 30):
        """
        Initialize the Bible Character agent.
        
        Args:
            llm_client: The LLM client instance for making API calls
            session_timeout_minutes: Timeout duration for inactive sessions
        """
        self.llm_client = llm_client
        self.character_contexts: Dict[str, CharacterContext] = {}
        self.conversation_memories: Dict[str, ConversationMemory] = {}
        self.user_sessions: Dict[str, UserSession] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self._cleanup_task = None
        self.system_prompt = get_system_prompt()
        logger.info("BibleCharacter agent initialized successfully")

    async def start(self):
        """Start the cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_inactive_sessions())
            logger.info("Cleanup task started")

    async def stop(self):
        """Stop the cleanup task."""
        if self._cleanup_task is not None:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("Cleanup task stopped")

    async def _cleanup_inactive_sessions(self):
        """Periodically clean up inactive sessions."""
        while True:
            await asyncio.sleep(60)  # Check every minute
            current_time = datetime.utcnow()
            
            # Find and remove inactive sessions
            inactive_sessions = [
                user_id for user_id, session in self.user_sessions.items()
                if current_time - session.last_activity > self.session_timeout
            ]
            
            for user_id in inactive_sessions:
                await self._clear_user_session(user_id)
                logger.info(f"Cleared inactive session for user: {user_id}")

    async def _clear_user_session(self, user_id: str):
        """Clear all session data for a user."""
        # Remove user session
        self.user_sessions.pop(user_id, None)
        
        # Remove all conversation memories for this user
        memories_to_remove = [
            key for key in self.conversation_memories.keys()
            if key.startswith(f"{user_id}_")
        ]
        for key in memories_to_remove:
            self.conversation_memories.pop(key, None)
        
        logger.info(f"Cleared all session data for user: {user_id}")

    def _get_or_create_session(self, user_id: str) -> UserSession:
        """Get existing session or create new one."""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = UserSession(
                user_id=user_id,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            logger.info(f"Created new session for user: {user_id}")
        else:
            # Update last activity
            self.user_sessions[user_id].last_activity = datetime.utcnow()
        
        return self.user_sessions[user_id]

    async def get_character_context(self, character_name: str) -> CharacterContext:
        """
        Extract and store character information if not already cached.
        
        Args:
            character_name (str): Name of the biblical character
            
        Returns:
            CharacterContext: The character's context information
        """
        # Return cached context if available
        if character_name in self.character_contexts:
            logger.info(f"Using cached context for character: {character_name}")
            return self.character_contexts[character_name]

        logger.info(f"Extracting new context for character: {character_name}")
        
        # Chain 1: Extract new context
        prompt = get_character_prompt(character_name)
        response = self.llm_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse and structure the response
        context = CharacterContext(
            name=character_name,
            biographical_info=self._parse_biographical_info(response.choices[0].message.content),
            key_events=self._parse_key_events(response.choices[0].message.content),
            character_traits=self._parse_character_traits(response.choices[0].message.content),
            legacy=self._parse_legacy(response.choices[0].message.content),
            bible_verses=self._parse_bible_verses(response.choices[0].message.content),
            extracted_at=datetime.utcnow()
        )
        
        # Cache the context
        self.character_contexts[character_name] = context
        logger.info(f"Successfully extracted and cached context for character: {character_name}")
        return context

    async def chat_with_character(
        self, 
        user_id: str, 
        character_name: str, 
        message: str
    ) -> str:
        """
        Generate a response from the character's perspective.
        
        Args:
            user_id (str): Unique identifier for the user
            character_name (str): Name of the biblical character
            message (str): User's message
            
        Returns:
            str: Character's response
        """
        try:
            # Update or create user session
            self._get_or_create_session(user_id)
            
            # Get or create conversation memory
            memory = self.get_or_create_memory(user_id, character_name)
            
            # Get character context (cached or newly extracted)
            context = await self.get_character_context(character_name)
            
            # Add user message to memory
            memory.add_message("user", message)
            
            # Chain 2: Generate response using context and conversation history
            prompt = get_response_prompt(
                character_name=character_name,
                character_context=context.to_dict(),
                conversation_history=memory.get_formatted_history(),
                user_message=message
            )
            
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            character_response = response.choices[0].message.content
            
            # Add character response to memory
            memory.add_message("assistant", character_response)
            
            logger.info(f"Generated response for user {user_id} from character {character_name}")
            return character_response
            
        except Exception as e:
            logger.error(f"Error in chat_with_character: {str(e)}")
            raise

    def get_or_create_memory(
        self, 
        user_id: str, 
        character_name: str
    ) -> ConversationMemory:
        """
        Get existing conversation memory or create new one.
        
        Args:
            user_id (str): Unique identifier for the user
            character_name (str): Name of the biblical character
            
        Returns:
            ConversationMemory: The conversation memory
        """
        memory_key = f"{user_id}_{character_name}"
        
        if memory_key in self.conversation_memories:
            return self.conversation_memories[memory_key]
        
        memory = ConversationMemory(
            user_id=user_id,
            character_name=character_name,
            messages=deque(maxlen=16),  # 8 exchanges * 2 messages per exchange
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        self.conversation_memories[memory_key] = memory
        logger.info(f"Created new conversation memory for user {user_id} with character {character_name}")
        return memory

    def _parse_biographical_info(self, response: str) -> Dict[str, str]:
        """Parse biographical information from LLM response."""
        try:
            # Extract the biographical section
            bio_section = response.split("Biographical Information:")[1].split("Key Events:")[0].strip()
            bio_items = [item.strip() for item in bio_section.split("\n") if item.strip()]
            
            bio_dict = {}
            for item in bio_items:
                if ":" in item:
                    key, value = item.split(":", 1)
                    # Clean up the key by removing any markdown formatting
                    key = key.replace("*", "").replace("-", "").strip()
                    bio_dict[key] = value.strip()
            
            return bio_dict
        except Exception as e:
            logger.error(f"Error parsing biographical info: {str(e)}")
            return {
                "Época y lugar": "Información no disponible",
                "Antecedentes familiares": "Información no disponible",
                "Ocupación principal": "Información no disponible"
            }

    def _parse_key_events(self, response: str) -> List[str]:
        """Parse key events from LLM response."""
        try:
            # Extract the key events section
            events_section = response.split("Key Events:")[1].split("Character Traits:")[0].strip()
            events = []
            for line in events_section.split("\n"):
                line = line.strip()
                if line and not line.startswith("-") and not line.startswith("###"):
                    # Clean up the event by removing any markdown formatting
                    event = line.replace("*", "").strip()
                    if event:
                        events.append(event)
            return events
        except Exception as e:
            logger.error(f"Error parsing key events: {str(e)}")
            return ["Información no disponible"]

    def _parse_character_traits(self, response: str) -> Dict[str, str]:
        """Parse character traits from LLM response."""
        try:
            # Extract the character traits section
            traits_section = response.split("Character Traits:")[1].split("Legacy:")[0].strip()
            traits_items = [item.strip() for item in traits_section.split("\n") if item.strip()]
            
            traits_dict = {}
            for item in traits_items:
                if ":" in item:
                    key, value = item.split(":", 1)
                    # Clean up the key by removing any markdown formatting
                    key = key.replace("*", "").replace("-", "").strip()
                    traits_dict[key] = value.strip()
            
            return traits_dict
        except Exception as e:
            logger.error(f"Error parsing character traits: {str(e)}")
            return {
                "Rasgos principales": "Información no disponible",
                "Fortalezas": "Información no disponible",
                "Debilidades": "Información no disponible",
                "Relación con Dios": "Información no disponible"
            }

    def _parse_legacy(self, response: str) -> Dict[str, str]:
        """Parse legacy information from LLM response."""
        try:
            # Extract the legacy section
            legacy_section = response.split("Legacy:")[1].split("Bible Verses:")[0].strip()
            legacy_items = [item.strip() for item in legacy_section.split("\n") if item.strip()]
            
            legacy_dict = {}
            for item in legacy_items:
                if ":" in item:
                    key, value = item.split(":", 1)
                    # Clean up the key by removing any markdown formatting
                    key = key.replace("*", "").replace("-", "").strip()
                    legacy_dict[key] = value.strip()
            
            return legacy_dict
        except Exception as e:
            logger.error(f"Error parsing legacy: {str(e)}")
            return {
                "Influencia histórica": "Información no disponible",
                "Lecciones principales": "Información no disponible",
                "Importancia bíblica": "Información no disponible"
            }

    def _parse_bible_verses(self, response: str) -> List[str]:
        """Parse Bible verses from LLM response."""
        try:
            # Extract the Bible verses section
            verses_section = response.split("Bible Verses:")[1].strip()
            verses = []
            for line in verses_section.split("\n"):
                line = line.strip()
                if line and not line.startswith("-") and not line.startswith("###"):
                    # Clean up the verse by removing any markdown formatting
                    verse = line.replace("*", "").strip()
                    if verse:
                        verses.append(verse)
            return verses
        except Exception as e:
            logger.error(f"Error parsing Bible verses: {str(e)}")
            return ["Información no disponible"] 