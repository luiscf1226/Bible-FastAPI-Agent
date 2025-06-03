from services.feeling import FeelingService
from dtos.feeling_conversation import FeelingResponse, FeelingConversation
from typing import Optional

class FeelingController:
    def __init__(self):
        self.service = FeelingService()

    def process_feeling(self, conversation_id: str, feeling: str, text: str, include_svg: bool = False) -> FeelingResponse:
        """
        Process a feeling message and generate a response.
        
        Args:
            conversation_id (str): The conversation ID
            feeling (str): The feeling to process
            text (str): The text context
            include_svg (bool): Whether to include a motivational SVG
            
        Returns:
            FeelingResponse: The processed feeling response
        """
        return self.service.process_feeling(
            conversation_id=conversation_id,
            feeling=feeling,
            text=text,
            include_svg=include_svg
        )

    def get_conversation(self, conversation_id: str) -> FeelingConversation:
        """
        Get a conversation by its ID.
        
        Args:
            conversation_id (str): The conversation ID
            
        Returns:
            FeelingConversation: The conversation if found
        """
        return self.service.get_conversation(conversation_id) 