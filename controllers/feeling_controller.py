from services.feeling import FeelingService
from dtos.feeling_conversation import FeelingResponse, FeelingConversation
from typing import Optional

class FeelingController:
    def __init__(self):
        self.service = FeelingService()

    def process_feeling(self, conversation_id: str, feeling: str, text: str) -> FeelingResponse:
        return self.service.process_feeling(conversation_id, feeling, text)

    def get_conversation(self, conversation_id: str) -> Optional[FeelingConversation]:
        return self.service.get_conversation(conversation_id) 