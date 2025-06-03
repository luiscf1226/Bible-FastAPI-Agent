from typing import List
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dtos.prayer_petition import PrayerPetitionRequest, PrayerPetitionResponse
from .prompts.prayer_petition_agent import PRAYER_PETITION_SYSTEM_PROMPT, PRAYER_PETITION_PROMPT
import json
import logging

logger = logging.getLogger(__name__)

class PrayerPetitionAgent:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.7,
            max_tokens=1000,  # Ensure enough tokens for complete response
            request_timeout=30  # Increase timeout for complete responses
        )
    
    async def process_petition(self, request: PrayerPetitionRequest) -> PrayerPetitionResponse:
        """
        Procesa una petición de oración y devuelve versículos bíblicos relevantes y una oración
        """
        try:
            # Create messages for the chat
            messages = [
                SystemMessage(content=PRAYER_PETITION_SYSTEM_PROMPT),
                HumanMessage(content=PRAYER_PETITION_PROMPT.format(
                    petition=request.petition
                ))
            ]
            
            # Get response from the model
            response = await self.llm.agenerate([messages])
            result = response.generations[0][0].text.strip()
            
            # Try to parse JSON response
            try:
                parsed_response = json.loads(result)
                
                # Validate required fields
                if not all(key in parsed_response for key in ["bible_verses", "prayer", "explanation"]):
                    raise ValueError("Missing required fields in response")
                
                # Ensure bible_verses is a list with at least one verse
                if not isinstance(parsed_response["bible_verses"], list) or not parsed_response["bible_verses"]:
                    raise ValueError("Invalid or empty bible verses")
                
                return PrayerPetitionResponse(
                    bible_verses=parsed_response["bible_verses"],
                    prayer=parsed_response["prayer"],
                    explanation=parsed_response["explanation"]
                )
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Raw response: {result}")
                raise ValueError("Invalid response format from AI model")
                
        except Exception as e:
            logger.error(f"Error processing prayer petition: {str(e)}")
            raise ValueError(f"Error processing prayer petition: {str(e)}") 