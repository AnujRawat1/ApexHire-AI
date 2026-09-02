import pytest
from app.config.settings import Settings
from app.exceptions.ai_exceptions import AIProviderException
from app.services.provider_service import ProviderService


def test_provider_service_unsupported_provider():
    settings = Settings(
        AI_PROVIDER="unsupported_provider",
        GEMINI_API_KEY="mock-gemini-key",
        GROQ_API_KEY="mock-groq-key",
    )
    service = ProviderService(settings)
    with pytest.raises(AIProviderException) as exc_info:
        service.get_llm(provider="unsupported_provider")
    assert "Unsupported AI provider" in str(exc_info.value)


def test_provider_service_missing_gemini_key():
    settings = Settings(
        AI_PROVIDER="gemini",
        GEMINI_API_KEY=None,
        GROQ_API_KEY="mock-groq-key",
    )
    service = ProviderService(settings)
    with pytest.raises(AIProviderException) as exc_info:
        service.get_llm(provider="gemini")
    assert "GEMINI_API_KEY is not configured" in str(exc_info.value)


def test_provider_service_missing_groq_key():
    settings = Settings(
        AI_PROVIDER="groq",
        GEMINI_API_KEY="mock-gemini-key",
        GROQ_API_KEY=None,
    )
    service = ProviderService(settings)
    with pytest.raises(AIProviderException) as exc_info:
        service.get_llm(provider="groq")
    assert "GROQ_API_KEY is not configured" in str(exc_info.value)


def test_fallback_provider_resolution():
    settings = Settings(
        ENABLE_PROVIDER_FALLBACK=True,
        GEMINI_API_KEY="mock-gemini-key",
        GROQ_API_KEY="mock-groq-key",
    )
    service = ProviderService(settings)
    assert service.get_fallback_provider("gemini") == "groq"
    assert service.get_fallback_provider("groq") == "gemini"


def test_fallback_provider_disabled():
    settings = Settings(
        ENABLE_PROVIDER_FALLBACK=False,
        GEMINI_API_KEY="mock-gemini-key",
        GROQ_API_KEY="mock-groq-key",
    )
    service = ProviderService(settings)
    assert service.get_fallback_provider("gemini") is None
