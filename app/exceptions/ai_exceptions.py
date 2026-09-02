from typing import Optional


class AIServiceException(Exception):
    """Base exception for all AI Service related errors."""

    def __init__(self, message: str, code: str = "AI_SERVICE_ERROR", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class InvalidAnalysisRequestException(AIServiceException):
    """Raised when an incoming analysis request fails domain validation."""

    def __init__(self, message: str = "Invalid analysis request parameters."):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=400)


class UnauthorizedException(AIServiceException):
    """Raised when client fails service API key authentication."""

    def __init__(self, message: str = "Invalid or missing service authentication credentials."):
        super().__init__(message=message, code="UNAUTHORIZED", status_code=401)


class ForbiddenException(AIServiceException):
    """Raised when client is forbidden from accessing the service."""

    def __init__(self, message: str = "Access to this AI resource is forbidden."):
        super().__init__(message=message, code="FORBIDDEN", status_code=403)


class AIProviderException(AIServiceException):
    """Raised when an upstream LLM provider encounters an error."""

    def __init__(self, message: str = "LLM provider encountered an error during analysis.", provider: Optional[str] = None):
        detail = f"{message} (Provider: {provider})" if provider else message
        super().__init__(message=detail, code="AI_PROVIDER_ERROR", status_code=502)
        self.provider = provider


class AIProviderTimeoutException(AIServiceException):
    """Raised when an LLM provider request times out."""

    def __init__(self, message: str = "AI analysis request timed out with upstream provider.", provider: Optional[str] = None):
        detail = f"{message} (Provider: {provider})" if provider else message
        super().__init__(message=detail, code="AI_PROVIDER_TIMEOUT", status_code=504)
        self.provider = provider


class AIProviderRateLimitException(AIServiceException):
    """Raised when an LLM provider rate limit is exceeded."""

    def __init__(self, message: str = "AI provider rate limit exceeded. Please retry shortly.", provider: Optional[str] = None):
        detail = f"{message} (Provider: {provider})" if provider else message
        super().__init__(message=detail, code="AI_RATE_LIMITED", status_code=429)
        self.provider = provider


class AIResponseValidationException(AIServiceException):
    """Raised when the LLM returns output that cannot be parsed into the expected schema."""

    def __init__(self, message: str = "AI model returned an invalid or unparseable structured response."):
        super().__init__(message=message, code="AI_RESPONSE_INVALID", status_code=502)
