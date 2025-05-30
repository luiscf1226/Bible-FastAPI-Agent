from fastapi import APIRouter, HTTPException, Depends, Request, Response
from dtos.feeling_conversation import FeelingMessage, FeelingResponse, FeelingConversation
from controllers.feeling_controller import FeelingController
from core.dependencies import create_rate_limit_dependency
from typing import Optional
import uuid

router = APIRouter(
    responses={
        404: {"description": "Not found"},
        429: {"description": "Too Many Requests"}
    }
)

# Create endpoint-specific rate limiters
check_feeling_process_rate_limit = create_rate_limit_dependency("feeling_process")
check_feeling_get_rate_limit = create_rate_limit_dependency("feeling_get")

def get_controller() -> FeelingController:
    return FeelingController()

@router.post("/feeling", response_model=FeelingResponse)
async def process_feeling(
    request: Request,
    response: Response,
    message: FeelingMessage,
    controller: FeelingController = Depends(get_controller),
    _: None = Depends(check_feeling_process_rate_limit)
):
    """
    Process a feeling message and generate a response.
    
    Args:
        request (Request): FastAPI request object
        response (Response): FastAPI response object
        message (FeelingMessage): The feeling message to process
        controller (FeelingController): The feeling controller instance
        
    Returns:
        FeelingResponse: The processed feeling response
    """
    try:
        conversation_id = str(uuid.uuid4())
        return controller.process_feeling(
            conversation_id=conversation_id,
            feeling=message.feeling,
            text=message.text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feeling/{conversation_id}", response_model=Optional[FeelingConversation])
async def get_conversation(
    request: Request,
    response: Response,
    conversation_id: str,
    controller: FeelingController = Depends(get_controller),
    _: None = Depends(check_feeling_get_rate_limit)
):
    """
    Get a conversation by its ID.
    
    Args:
        request (Request): FastAPI request object
        response (Response): FastAPI response object
        conversation_id (str): The ID of the conversation to retrieve
        controller (FeelingController): The feeling controller instance
        
    Returns:
        Optional[FeelingConversation]: The conversation if found, None otherwise
    """
    try:
        conversation = controller.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 