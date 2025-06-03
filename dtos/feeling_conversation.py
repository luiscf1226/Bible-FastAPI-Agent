from pydantic import BaseModel, Field
from typing import List, Optional

class FeelingMessage(BaseModel):
    feeling: str = Field(..., description="The feeling or emotion being expressed")
    text: str = Field(..., description="Additional context or description of the feeling")
    include_svg: bool = Field(
        default=False,
        description="Whether to include a motivational SVG graphic in the response"
    )

class FeelingResponse(BaseModel):
    verse: str = Field(..., description="The Bible verse that addresses the feeling")
    devotional: str = Field(..., description="A devotional message based on the feeling and verse")
    svg: Optional[str] = Field(
        default=None,
        description="Optional SVG string containing a motivational graphic"
    )

class FeelingConversation(BaseModel):
    messages: List[FeelingMessage] = Field(..., description="List of messages in the conversation")
    response: Optional[FeelingResponse] = Field(
        default=None,
        description="The response to the last message in the conversation"
    ) 