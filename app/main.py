import time
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import get_settings
from app.exceptions.handlers import register_exception_handlers
from app.utils.logging import setup_logging, request_id_ctx
from app.api.routes.health import health_router
from app.api.routes.resume import resume_router

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware for injecting correlation ID and logging request lifecycle."""

    async def dispatch(self, request: Request, call_next):
        # Extract existing X-Request-ID or generate new UUID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_ctx.set(request_id)
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            response.headers["X-Request-ID"] = request_id
            logger.info(
                f"{request.method} {request.url.path} -> status={response.status_code} "
                f"duration={duration_ms:.2f}ms"
            )
            return response
        finally:
            request_id_ctx.reset(token)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    settings = get_settings()
    setup_logging(log_level=settings.log_level)
    logger.info(
        f"Starting {settings.app_name} (Environment: {settings.app_env}) on "
        f"http://{settings.host}:{settings.port}"
    )
    logger.info(
        f"Default AI Provider: {settings.ai_provider} (Model: {settings.get_effective_model()})"
    )
    yield
    logger.info(f"Shutting down {settings.app_name}...")


def create_app() -> FastAPI:
    """Factory creating and configuring the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title="ApexHire AI Service",
        description=(
            "Internal AI processing service for ApexHire / ApexResume platform. "
            "Executes LangGraph workflows for resume analysis with Gemini and Groq."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Register Middlewares
    app.add_middleware(RequestContextMiddleware)

    cors_origins = settings.cors_origins_list
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )

    # Register Global Exception Handlers
    register_exception_handlers(app)

    # Register API Routers
    app.include_router(health_router)
    app.include_router(resume_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.app_env == "development",
    )
