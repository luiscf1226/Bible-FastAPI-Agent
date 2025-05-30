from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from dtos.bible_verse import BibleVerseResponse
from services.bible_verse import BibleVerseService
from core.dependencies import create_rate_limit_dependency

router = APIRouter(
    prefix="/verses",
    tags=["verses"],
    responses={
        400: {"description": "Bad Request"},
        429: {"description": "Too Many Requests"},
        500: {"description": "Internal Server Error"}
    }
)

# Create endpoint-specific rate limiter
check_verse_rate_limit = create_rate_limit_dependency("bible_verse_explain")

@router.post("/explain", response_model=BibleVerseResponse)
async def explain_verses(
    request: Request,
    response: Response,
    verses: List[str],
    verse_texts: Optional[List[str]] = None,
    _: None = Depends(check_verse_rate_limit)
) -> BibleVerseResponse:
    """
    Get a unified explanation for a list of Bible verses.
    
    Args:
        request (Request): FastAPI request object for getting client IP
        response (Response): FastAPI response object for setting headers
        verses (List[str]): List of verse references (e.g., ["Josue 1:9", "Filipenses 4:13"])
        verse_texts (Optional[List[str]]): Optional list of verse texts
        
    Returns:
        BibleVerseResponse: Contains the explanation and processed verses
        
    Raises:
        HTTPException: If there's an error processing the request or rate limit exceeded
    """
    try:
        service = BibleVerseService()
        return await service.explain_verses(verses=verses, verse_texts=verse_texts)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing verses") 