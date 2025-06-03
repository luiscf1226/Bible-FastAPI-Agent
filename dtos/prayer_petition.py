from pydantic import BaseModel
from typing import List, Optional

class PrayerPetitionRequest(BaseModel):
    petition: str

class PrayerPetitionResponse(BaseModel):
    bible_verses: List[str]
    prayer: str
    explanation: Optional[str] = None 