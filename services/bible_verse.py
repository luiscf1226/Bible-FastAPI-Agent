from typing import List, Optional
from agents.bible_verse import BibleVerseAgent
from dtos.bible_verse import BibleVerseRequest, BibleVerseResponse
from services.base import ServiceBase

class BibleVerseService(ServiceBase):
    def __init__(self):
        super().__init__()
        self.agent = BibleVerseAgent()

    async def explain_verses(
        self,
        verses: List[str],
        verse_texts: Optional[List[str]] = None
    ) -> BibleVerseResponse:
        """
        Process a list of Bible verses and provide a unified explanation.
        
        Args:
            verses (List[str]): List of verse references (e.g., ["Josue 1:9", "Filipenses 4:13"])
            verse_texts (Optional[List[str]]): Optional list of verse texts
            
        Returns:
            BibleVerseResponse: Contains the explanation and processed verses
            
        Raises:
            ValueError: If the number of verse texts doesn't match the number of verses
        """
        try:
            # Validate input
            if verse_texts and len(verse_texts) != len(verses):
                raise ValueError("Number of verse texts must match number of verses")

            # Create request
            request = BibleVerseRequest(
                verses=verses,
                verse_texts=verse_texts
            )

            # Get explanation from agent
            response = await self.agent.explain_verses(request)

            # Log successful processing
            self.logger.info(
                f"Successfully processed {len(verses)} verses",
                extra={
                    "verses": verses,
                    "has_texts": bool(verse_texts)
                }
            )

            return response

        except Exception as e:
            # Log error and re-raise
            self.logger.error(
                f"Error processing verses: {str(e)}",
                extra={
                    "verses": verses,
                    "error": str(e)
                }
            )
            raise 