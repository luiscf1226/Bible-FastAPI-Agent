from fastapi import APIRouter, HTTPException, Depends, Request, Response
from dtos.feeling_conversation import FeelingMessage, FeelingResponse, FeelingConversation
from controllers.feeling_controller import FeelingController
from typing import Optional
import uuid

router = APIRouter(
    responses={
        404: {"description": "Not found"}
    }
)

def get_controller() -> FeelingController:
    return FeelingController()

@router.post("/feeling", response_model=FeelingResponse)
async def process_feeling(
    request: Request,
    response: Response,
    message: FeelingMessage,
    controller: FeelingController = Depends(get_controller)
):
    """
    Process a feeling message and generate a response.
    
    Args:
        request (Request): FastAPI request object
        response (Response): FastAPI response object
        message (FeelingMessage): The feeling message to process, including whether to include an SVG
        controller (FeelingController): The feeling controller instance
        
    Returns:
        FeelingResponse: The processed feeling response
    """
    try:
        conversation_id = str(uuid.uuid4())
        return controller.process_feeling(
            conversation_id=conversation_id,
            feeling=message.feeling,
            text=message.text,
            include_svg=message.include_svg
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feeling/{conversation_id}", response_model=Optional[FeelingConversation])
async def get_conversation(
    request: Request,
    response: Response,
    conversation_id: str,
    controller: FeelingController = Depends(get_controller)
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