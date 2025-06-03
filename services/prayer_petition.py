from typing import Optional
from dtos.prayer_petition import PrayerPetitionRequest, PrayerPetitionResponse
from agents.prayer_petition import PrayerPetitionAgent
from .base import ServiceBase

class PrayerPetitionService(ServiceBase):
    def __init__(self):
        super().__init__()
        self.agent = PrayerPetitionAgent()

    async def process_petition(self, request: PrayerPetitionRequest) -> PrayerPetitionResponse:
        """
        Process a prayer petition and return a response with Bible verses and prayer
        """
        try:
            # Get response from the agent
            response = await self.agent.process_petition(request)
            return response

        except Exception as e:
            self.logger.error(f"Error processing prayer petition: {str(e)}")
            raise 