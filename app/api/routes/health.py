from fastapi import APIRouter, status
from app.config.settings import get_settings
from app.models.responses import HealthResponse

health_router = APIRouter(tags=["Health & Diagnostics"])


@health_router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Returns the operational health status of the AI service.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="healthy")


@health_router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Validates provider configuration and service readiness.",
)
async def readiness_check() -> dict:
    settings = get_settings()
    configured_providers = []
    if settings.gemini_api_key:
        configured_providers.append("gemini")
    if settings.groq_api_key:
        configured_providers.append("groq")

    return {
        "status": "ready",
        "primary_provider": settings.ai_provider,
        "configured_providers": configured_providers,
        "environment": settings.app_env,
    }
