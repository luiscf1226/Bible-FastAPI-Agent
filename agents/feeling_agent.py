from typing import List, Optional, Dict
from dtos.feeling_conversation import FeelingMessage, FeelingResponse, FeelingConversation
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
import json
from .prompts.feeling_agent import (
    FEELING_AGENT_SYSTEM_PROMPT,
    get_verse_prompt,
    get_devotional_prompt,
    get_conversation_prompt,
    get_feeling_identification_prompt,
    EMOTIONAL_RESPONSE_TEMPLATES
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class FeelingAgent:
    def __init__(self):
        self.conversations: dict[str, FeelingConversation] = {}
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info("FeelingAgent initialized successfully")

    def _get_ai_response(self, prompt: str, system_prompt: str = FEELING_AGENT_SYSTEM_PROMPT, retry_count: int = 3) -> str:
        for attempt in range(retry_count):
            try:
                logger.info(f"Attempting OpenAI API call (attempt {attempt + 1}/{retry_count})")
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                result = response.choices[0].message.content.strip()
                logger.info("Successfully received response from OpenAI API")
                return result
            except Exception as e:
                logger.error(f"Error during OpenAI API call: {str(e)}")
                if attempt < retry_count - 1:
                    continue
                return "Error al conectar con el servicio. Por favor, verifica tu conexión e intenta de nuevo."

    def _analyze_feeling(self, text: str) -> Dict:
        """Analyze the text to identify feelings and emotional context."""
        prompt = get_feeling_identification_prompt(text)
        response = self._get_ai_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to parse feeling analysis response")
            return {
                "sentimiento_primario": "indeterminado",
                "sentimientos_secundarios": [],
                "intensidad": "media",
                "necesidad_emocional": "acompañamiento",
                "tono_recomendado": "empático",
                "urgencia": "gradual"
            }

    def _get_conversation_history(self, conversation_id: str) -> str:
        """Format conversation history for context."""
        if conversation_id not in self.conversations:
            return ""
        
        history = []
        for msg in self.conversations[conversation_id].messages:
            history.append(f"Usuario: {msg.text}")
            if msg.response:
                history.append(f"Asistente: {msg.response.devotional}")
        
        return "\n".join(history)

    def process_message(self, conversation_id: str, text: str) -> FeelingResponse:
        try:
            # Initialize or get conversation
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = FeelingConversation(messages=[])
            
            # Analyze feelings
            feeling_analysis = self._analyze_feeling(text)
            feeling = feeling_analysis["sentimiento_primario"]
            
            # Create message
            message = FeelingMessage(feeling=feeling, text=text)
            self.conversations[conversation_id].messages.append(message)
            
            logger.info(f"Processing message for feeling: {feeling}")
            
            # Get conversation history
            conversation_history = self._get_conversation_history(conversation_id)
            
            # Get verse using AI
            verse_prompt = get_verse_prompt(feeling, text, conversation_history)
            verse = self._get_ai_response(verse_prompt)
            
            # Get devotional using AI
            devotional_prompt = get_devotional_prompt(feeling, text, verse, conversation_history)
            devotional = self._get_ai_response(devotional_prompt)
            
            response = FeelingResponse(verse=verse, devotional=devotional)
            self.conversations[conversation_id].response = response
            
            logger.info("Successfully processed message and generated response")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

    def continue_conversation(self, conversation_id: str, user_response: str) -> FeelingResponse:
        """Continue an existing conversation with a new user response."""
        try:
            if conversation_id not in self.conversations:
                raise ValueError("Conversation not found")
            
            conversation = self.conversations[conversation_id]
            if not conversation.messages:
                raise ValueError("No previous messages in conversation")
            
            # Get the original context
            original_message = conversation.messages[0]
            original_verse = conversation.response.verse if conversation.response else ""
            
            # Get conversation history
            conversation_history = self._get_conversation_history(conversation_id)
            
            # Generate continuation prompt
            continuation_prompt = get_conversation_prompt(
                original_message.feeling,
                original_message.text,
                original_verse,
                conversation_history,
                user_response
            )
            
            # Get AI response
            devotional = self._get_ai_response(continuation_prompt)
            
            # Create response
            response = FeelingResponse(verse=original_verse, devotional=devotional)
            conversation.response = response
            
            return response
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {str(e)}")
            raise

    def get_conversation_history(self, conversation_id: str) -> Optional[FeelingConversation]:
        """Get the complete conversation history."""
        return self.conversations.get(conversation_id) 