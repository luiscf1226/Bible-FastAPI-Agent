from typing import List, Optional
from pydantic import BaseModel

class BibleVerseRequest(BaseModel):
    verses: List[str]  # List of verse references like "Josue 1:9"
    verse_texts: Optional[List[str]] = None  # Optional list of verse texts

class BibleVerseResponse(BaseModel):
    explanation: str  # Single explanation for all verses
    verses: List[str]  # List of processed verses
    verse_texts: List[str]  # List of verse texts 