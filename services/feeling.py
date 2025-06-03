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
        
        Please provide a complete response with:
        1. A Bible verse that directly addresses this feeling
        2. The verse must be in Spanish
        3. Include the complete reference (Book, Chapter, and Verse)
        4. Keep it concise but ensure it's a complete verse
        5. If possible, include a brief explanation of why this verse is relevant
        
        Format: [Book] [Chapter]:[Verse] - [Complete verse text in Spanish]
        Explanation: [Brief explanation of relevance]"""

    def _get_devotional_prompt(self, feeling: str, text: str, verse: str) -> str:
        return f"""Based on the following feeling, context, and Bible verse, provide a complete devotional message in Spanish:
        Feeling: {feeling}
        Context: {text}
        Bible Verse: {verse}
        
        Please provide a complete response with:
        1. A well-structured devotional message (2-3 paragraphs)
        2. The message must be in Spanish
        3. Include:
           - An encouraging opening
           - Connection to the Bible verse
           - Practical application
           - A hopeful conclusion
        4. Make it personal and relatable
        5. Ensure the response is complete and meaningful
        
        Format:
        [Opening paragraph]
        [Main message connecting verse to feeling]
        [Practical application and conclusion]"""

    def _get_ai_response(self, prompt: str, retry_count: int = 3) -> str:
        for attempt in range(retry_count):
            try:
                logger.info(f"Attempting OpenAI API call (attempt {attempt + 1}/{retry_count})")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that provides Bible verses and devotionals in Spanish. Always provide complete responses."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                    presence_penalty=0.6,
                    frequency_penalty=0.3,
                    top_p=0.9
                )
                result = response.choices[0].message.content.strip()
                
                if not result or len(result) < 50:
                    logger.warning(f"Incomplete response received: {result}")
                    if attempt < retry_count - 1:
                        continue
                    return "Lo siento, no pude generar una respuesta completa. Por favor, intenta de nuevo."
                
                if result.endswith("...") or result.endswith("..") or result.endswith(".") == False:
                    logger.warning(f"Response appears incomplete: {result}")
                    if attempt < retry_count - 1:
                        continue
                
                logger.info("Successfully received complete response from OpenAI API")
                return result
            except Exception as e:
                logger.error(f"Error during OpenAI API call: {str(e)}")
                if attempt < retry_count - 1:
                    continue
                return "Error al conectar con el servicio. Por favor, verifica tu conexión e intenta de nuevo."

    def _generate_motivational_svg(self, verse: str, feeling: str, text: str = "") -> str:
        """
        Generate a motivational SVG based on the verse, feeling, and context.
        
        Args:
            verse (str): The Bible verse
            feeling (str): The user's feeling
            text (str): The context text
            
        Returns:
            str: SVG string with motivational design
        """
        # Process text for display
        def truncate_text(text: str, max_length: int = 100) -> str:
            if len(text) <= max_length:
                return text
            return text[:max_length] + "..."

        # Extract verse reference and content
        verse_parts = verse.split(" - ", 1)
        verse_ref = verse_parts[0] if len(verse_parts) > 1 else ""
        verse_content = verse_parts[1] if len(verse_parts) > 1 else verse
        
        # Process text for display
        display_text = truncate_text(text)
        display_verse = truncate_text(verse_content, 150)
        
        # Create a more comprehensive SVG
        svg = f'''<svg width="500" height="400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 400">
            <defs>
                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#4a90e2;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#2c3e50;stop-opacity:1" />
                </linearGradient>
                <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                    <feDropShadow dx="2" dy="2" stdDeviation="2" flood-opacity="0.3"/>
                </filter>
                <style>
                    .title {{ font-family: Arial; font-size: 24px; font-weight: bold; fill: white; }}
                    .subtitle {{ font-family: Arial; font-size: 18px; fill: white; }}
                    .content {{ font-family: Arial; font-size: 16px; fill: white; }}
                    .verse {{ font-family: Arial; font-size: 16px; font-style: italic; fill: white; }}
                    .reference {{ font-family: Arial; font-size: 14px; fill: #a8c6fa; }}
                </style>
            </defs>
            
            <!-- Background with rounded corners -->
            <rect width="500" height="400" fill="url(#grad1)" rx="20" ry="20"/>
            
            <!-- Decorative elements -->
            <circle cx="50" cy="50" r="30" fill="white" fill-opacity="0.1"/>
            <circle cx="450" cy="350" r="40" fill="white" fill-opacity="0.1"/>
            
            <!-- Main content -->
            <g filter="url(#shadow)">
                <!-- Feeling section -->
                <text x="50%" y="15%" text-anchor="middle" class="title">
                    {feeling.upper()}
                </text>
                
                <!-- Context text -->
                <text x="50%" y="30%" text-anchor="middle" class="content" width="400">
                    {display_text}
                </text>
                
                <!-- Verse reference -->
                <text x="50%" y="45%" text-anchor="middle" class="reference">
                    {verse_ref}
                </text>
                
                <!-- Verse content -->
                <text x="50%" y="60%" text-anchor="middle" class="verse" width="400">
                    {display_verse}
                </text>
                
                <!-- Decorative waves -->
                <path d="M 50,300 Q 250,330 450,300" stroke="white" stroke-width="3" fill="none" stroke-linecap="round"/>
                <path d="M 100,320 Q 250,310 400,320" stroke="white" stroke-width="2" fill="none" stroke-linecap="round"/>
            </g>
            
            <!-- Responsive scaling -->
            <style>
                @media (max-width: 500px) {{
                    svg {{ width: 100%; height: auto; }}
                }}
            </style>
        </svg>'''
        
        return svg

    def process_feeling(self, conversation_id: str, feeling: str, text: str, include_svg: bool = False) -> FeelingResponse:
        try:
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = FeelingConversation(messages=[])
            
            message = FeelingMessage(feeling=feeling, text=text)
            self.conversations[conversation_id].messages.append(message)
            
            logger.info(f"Processing message for feeling: {feeling}")
            
            # Get verse using AI with retry logic
            verse_prompt = self._get_verse_prompt(feeling, text)
            verse = self._get_ai_response(verse_prompt)
            
            # Get devotional using AI with retry logic
            devotional_prompt = self._get_devotional_prompt(feeling, text, verse)
            devotional = self._get_ai_response(devotional_prompt)
            
            # Always generate SVG for consistency
            svg = self._generate_motivational_svg(verse, feeling, text)
            
            response = FeelingResponse(
                verse=verse,
                devotional=devotional,
                svg=svg if include_svg else None
            )
            self.conversations[conversation_id].response = response
            
            logger.info("Successfully processed message and generated complete response")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

    def get_conversation(self, conversation_id: str) -> Optional[FeelingConversation]:
        return self.conversations.get(conversation_id) 