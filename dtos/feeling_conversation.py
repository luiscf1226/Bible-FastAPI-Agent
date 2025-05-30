from pydantic import BaseModel
from typing import List, Optional

class FeelingMessage(BaseModel):
    feeling: str
    text: str

class FeelingResponse(BaseModel):
    verse: str
    devotional: str

class FeelingConversation(BaseModel):
    messages: List[FeelingMessage]
    response: Optional[FeelingResponse] = None 