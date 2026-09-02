import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.ai_exceptions import AIServiceException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers for the FastAPI application."""

    @app.exception_handler(AIServiceException)
    async def ai_service_exception_handler(request: Request, exc: AIServiceException) -> JSONResponse:
        logger.error(
            f"AIServiceException [{exc.code}] on {request.method} {request.url.path}: {exc.message}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Format field validation errors into a clear, single error message
        errors = exc.errors()
        messages = []
        for err in errors:
            loc = " -> ".join([str(l) for l in err.get("loc", []) if l != "body"])
            msg = err.get("msg", "Invalid value")
            messages.append(f"{loc}: {msg}" if loc else msg)
        combined_message = "; ".join(messages) if messages else "Invalid request payload."

        logger.warning(
            f"Validation error on {request.method} {request.url.path}: {combined_message}"
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Validation failed: {combined_message}",
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code_map = {
            400: "VALIDATION_ERROR",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            429: "AI_RATE_LIMITED",
            500: "INTERNAL_ERROR",
            502: "AI_PROVIDER_ERROR",
            503: "SERVICE_UNAVAILABLE",
            504: "AI_PROVIDER_TIMEOUT",
        }
        error_code = code_map.get(exc.status_code, "HTTP_ERROR")
        logger.warning(
            f"HTTP {exc.status_code} [{error_code}] on {request.method} {request.url.path}: {exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": error_code,
                    "message": str(exc.detail),
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal server error occurred while processing the resume analysis.",
                }
            },
        )
