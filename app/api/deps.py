import secrets
from typing import Optional
from fastapi import Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from app.config.settings import get_settings
from app.exceptions.ai_exceptions import UnauthorizedException

# Define OpenAPI security schemes for Swagger UI
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_service_api_key(
    bearer_credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    x_api_key: Optional[str] = Security(api_key_header_scheme),
) -> str:
    """FastAPI dependency to authenticate internal service-to-service calls.
    
    Accepts either:
    1. Authorization: Bearer <API_KEY>
    2. X-API-Key: <API_KEY>
    """
    settings = get_settings()
    expected_key = settings.ai_service_api_key

    provided_token: Optional[str] = None

    if bearer_credentials and bearer_credentials.credentials:
        provided_token = bearer_credentials.credentials.strip()
    elif x_api_key:
        provided_token = x_api_key.strip()

    if not provided_token:
        raise UnauthorizedException("Missing Authorization Bearer token or X-API-Key header.")

    # Use constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(provided_token, expected_key):
        raise UnauthorizedException("Invalid service API key provided.")

    return provided_token
