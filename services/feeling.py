from typing import Optional
from dtos.feeling_conversation import FeelingMessage, FeelingResponse, FeelingConversation
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
from services.base import BaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class FeelingService(BaseService):
    def __init__(self, model: str = "gpt-3.5-turbo"):
        super().__init__(model=model)
        self.conversations: dict[str, FeelingConversation] = {}
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info("FeelingService initialized successfully")

    def _get_verse_prompt(self, feeling: str, text: str) -> str:
        return f"""Based on the following feeling and context, provide a relevant Bible verse in Spanish:
        Feeling: {feeling}
        Context: {text}
        
        Please provide:
        1. A Bible verse that addresses this feeling
        2. The verse should be in Spanish
        3. Include the reference
        4. Keep it concise and relevant
        
        Format: [Book] [Chapter]:[Verse] - [Verse text in Spanish]"""

    def _get_devotional_prompt(self, feeling: str, text: str, verse: str) -> str:
        return f"""Based on the following feeling, context, and Bible verse, provide a short devotional message in Spanish:
        Feeling: {feeling}
        Context: {text}
        Bible Verse: {verse}
        
        Please provide:
        1. A short devotional message (1 paragraph max)
        2. The message should be in Spanish
        3. It should be encouraging and relevant to the feeling
        4. Include practical application
        5. Keep it personal and relatable"""

    def _get_ai_response(self, prompt: str, retry_count: int = 3) -> str:
        for attempt in range(retry_count):
            try:
                logger.info(f"Attempting OpenAI API call (attempt {attempt + 1}/{retry_count})")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that provides Bible verses and devotionals in Spanish."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
                result = response.choices[0].message.content.strip()
                logger.info("Successfully received response from OpenAI API")
                return result
            except Exception as e:
                logger.error(f"Error during OpenAI API call: {str(e)}")
                if attempt < retry_count - 1:
                    continue
                return "Error al conectar con el servicio. Por favor, verifica tu conexión e intenta de nuevo."

    def process_feeling(self, conversation_id: str, feeling: str, text: str) -> FeelingResponse:
        try:
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = FeelingConversation(messages=[])
            
            message = FeelingMessage(feeling=feeling, text=text)
            self.conversations[conversation_id].messages.append(message)
            
            logger.info(f"Processing message for feeling: {feeling}")
            
            # Get verse using AI
            verse_prompt = self._get_verse_prompt(feeling, text)
            verse = self._get_ai_response(verse_prompt)
            
            # Get devotional using AI
            devotional_prompt = self._get_devotional_prompt(feeling, text, verse)
            devotional = self._get_ai_response(devotional_prompt)
            
            response = FeelingResponse(verse=verse, devotional=devotional)
            self.conversations[conversation_id].response = response
            
            logger.info("Successfully processed message and generated response")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

    def get_conversation(self, conversation_id: str) -> Optional[FeelingConversation]:
        return self.conversations.get(conversation_id) 