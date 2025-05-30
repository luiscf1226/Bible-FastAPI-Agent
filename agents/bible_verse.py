from typing import List, Optional
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dtos.bible_verse import BibleVerseRequest, BibleVerseResponse
from .prompts.bible_verse_agent import BIBLE_VERSE_EXPLANATION_PROMPT, BIBLE_VERSE_SYSTEM_PROMPT

class BibleVerseAgent:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.llm = ChatOpenAI(model_name=model_name, temperature=0.7)
    
    async def explain_verses(self, request: BibleVerseRequest) -> BibleVerseResponse:
        # Format verses and texts for the prompt
        verses_text = "\n".join([f"- {verse}" for verse in request.verses])
        verse_texts = "\n".join([f"- {text}" for text in (request.verse_texts or [])])
        
        # Create messages for the chat
        messages = [
            SystemMessage(content=BIBLE_VERSE_SYSTEM_PROMPT),
            HumanMessage(content=BIBLE_VERSE_EXPLANATION_PROMPT.format(
                verses=verses_text,
                verse_texts=verse_texts
            ))
        ]
        
        # Get explanation from the model
        response = await self.llm.agenerate([messages])
        explanation = response.generations[0][0].text.strip()
        
        # Clean up explanation to remove verse references
        explanation = explanation.replace("Versículo:", "").replace("Versículos:", "")
        for verse in request.verses:
            explanation = explanation.replace(verse, "")
        
        # Clean up extra whitespace and newlines
        explanation = " ".join(explanation.split())
        
        return BibleVerseResponse(
            explanation=explanation,
            verses=request.verses,
            verse_texts=request.verse_texts or []
        ) 