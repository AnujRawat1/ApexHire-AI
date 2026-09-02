import logging
from fastapi import APIRouter, Depends, status
from app.api.deps import verify_service_api_key
from app.models.requests import ResumeAnalysisRequest
from app.models.responses import AnalysisResultResponse, ErrorResponse
from app.services.analysis_service import AnalysisService

logger = logging.getLogger(__name__)

resume_router = APIRouter(tags=["Resume Analysis"])

_analysis_service: AnalysisService | None = None


def get_analysis_service() -> AnalysisService:
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service


@resume_router.post(
    "/api/resume/analyze",
    response_model=AnalysisResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Resume",
    description="Primary endpoint for analyzing candidate resumes using the LangGraph AI workflow. Called by Spring Boot backend.",
    responses={
        200: {"model": AnalysisResultResponse, "description": "Successful structured resume analysis result"},
        400: {"model": ErrorResponse, "description": "Invalid request payload or validation failure"},
        401: {"model": ErrorResponse, "description": "Missing or invalid service API key"},
        429: {"model": ErrorResponse, "description": "AI provider rate limit exceeded"},
        502: {"model": ErrorResponse, "description": "AI provider failure or unparseable structured response"},
        504: {"model": ErrorResponse, "description": "AI provider analysis request timeout"},
    },
)
async def analyze_resume(
    request: ResumeAnalysisRequest,
    _auth: str = Depends(verify_service_api_key),
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisResultResponse:
    """Processes resume analysis request via LangGraph workflow."""
    return await service.analyze_resume(request)
