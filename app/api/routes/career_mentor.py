import logging
from fastapi import APIRouter, Depends, status
from app.api.deps import verify_service_api_key
from app.models.career_mentor import (
    CareerMentorChatRequest,
    CareerMentorChatResponse,
)
from app.models.responses import ErrorResponse
from app.services.career_mentor_service import CareerMentorService

logger = logging.getLogger(__name__)

career_mentor_router = APIRouter(tags=["AI Career Mentor"])

_career_mentor_service: CareerMentorService | None = None


def get_career_mentor_service() -> CareerMentorService:
    global _career_mentor_service
    if _career_mentor_service is None:
        _career_mentor_service = CareerMentorService()
    return _career_mentor_service


@career_mentor_router.post(
    "/api/career-mentor/chat",
    response_model=CareerMentorChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Career Mentor Chat",
    description="Processes multi-turn conversation with an executive AI career mentor with candidate context, goals, and role targeting.",
    responses={
        200: {"model": CareerMentorChatResponse, "description": "Successfully generated mentor response and follow-ups"},
        400: {"model": ErrorResponse, "description": "Invalid request payload or validation error"},
        401: {"model": ErrorResponse, "description": "Missing or invalid service API key"},
        429: {"model": ErrorResponse, "description": "AI provider rate limit exceeded"},
        502: {"model": ErrorResponse, "description": "AI provider failure or malformed response"},
        504: {"model": ErrorResponse, "description": "AI provider generation timeout"},
    },
)
async def chat_with_mentor(
    request: CareerMentorChatRequest,
    _auth: str = Depends(verify_service_api_key),
    service: CareerMentorService = Depends(get_career_mentor_service),
) -> CareerMentorChatResponse:
    """Interacts with the AI Career Mentor workflow."""
    return await service.chat(request)
