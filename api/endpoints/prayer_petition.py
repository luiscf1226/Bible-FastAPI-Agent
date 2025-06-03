from fastapi import APIRouter, HTTPException, Request, Response
from dtos.prayer_petition import PrayerPetitionRequest, PrayerPetitionResponse
from services.prayer_petition import PrayerPetitionService

router = APIRouter(
    prefix="/prayers",
    tags=["prayers"],
    responses={
        400: {"description": "Bad Request"},
        500: {"description": "Internal Server Error"}
    }
)

@router.post("/petition", response_model=PrayerPetitionResponse)
async def process_prayer_petition(
    request: Request,
    response: Response,
    petition: PrayerPetitionRequest
) -> PrayerPetitionResponse:
    """
    Process a prayer petition and return relevant Bible verses and a prayer.
    
    Args:
        request (Request): FastAPI request object for getting client IP
        response (Response): FastAPI response object for setting headers
        petition (PrayerPetitionRequest): The prayer petition to process
        
    Returns:
        PrayerPetitionResponse: Contains Bible verses, prayer, and explanation
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        service = PrayerPetitionService()
        return await service.process_petition(request=petition)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing prayer petition") 