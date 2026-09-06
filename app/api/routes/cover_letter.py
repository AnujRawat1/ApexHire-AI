import logging
from fastapi import APIRouter, Depends, status
from app.api.deps import verify_service_api_key
from app.models.requests import CoverLetterGenerateRequest
from app.models.responses import CoverLetterGenerateResponse, ErrorResponse
from app.services.cover_letter_service import CoverLetterService

logger = logging.getLogger(__name__)

cover_letter_router = APIRouter(tags=["Cover Letter Generation"])

_cover_letter_service: CoverLetterService | None = None


def get_cover_letter_service() -> CoverLetterService:
    global _cover_letter_service
    if _cover_letter_service is None:
        _cover_letter_service = CoverLetterService()
    return _cover_letter_service


@cover_letter_router.post(
    "/api/cover-letter/generate",
    response_model=CoverLetterGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Cover Letter",
    description="Generates a customized, high-converting cover letter based on role, company, tone, job description, and optional resume.",
    responses={
        200: {"model": CoverLetterGenerateResponse, "description": "Successfully generated cover letter"},
        400: {"model": ErrorResponse, "description": "Invalid request payload or validation error"},
        401: {"model": ErrorResponse, "description": "Missing or invalid service API key"},
        429: {"model": ErrorResponse, "description": "AI provider rate limit exceeded"},
        502: {"model": ErrorResponse, "description": "AI provider failure or malformed response"},
        504: {"model": ErrorResponse, "description": "AI provider generation timeout"},
    },
)
async def generate_cover_letter(
    request: CoverLetterGenerateRequest,
    _auth: str = Depends(verify_service_api_key),
    service: CoverLetterService = Depends(get_cover_letter_service),
) -> CoverLetterGenerateResponse:
    """Generates personalized cover letter via LLM service."""
    return await service.generate_cover_letter(request)
