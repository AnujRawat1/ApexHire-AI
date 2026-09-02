import pytest
from unittest.mock import AsyncMock, MagicMock
from pydantic import BaseModel

from app.config.settings import Settings
from app.exceptions.ai_exceptions import (
    AIProviderException,
    AIProviderTimeoutException,
    AIResponseValidationException,
)
from app.services.llm_service import LLMService
from app.services.provider_service import ProviderService


class DummySchema(BaseModel):
    name: str
    value: int


@pytest.mark.asyncio
async def test_llm_service_success():
    mock_provider = MagicMock(spec=ProviderService)
    mock_llm = MagicMock()
    mock_structured = AsyncMock()
    mock_structured.ainvoke.return_value = DummySchema(name="Test", value=100)
    mock_llm.with_structured_output.return_value = mock_structured
    mock_provider.get_llm.return_value = mock_llm

    settings = Settings(AI_PROVIDER="gemini", AI_MAX_RETRIES=1, AI_REQUEST_TIMEOUT=5)
    service = LLMService(provider_service=mock_provider, settings=settings)

    result = await service.generate_structured(
        schema=DummySchema,
        prompt="Test Prompt",
        provider="gemini",
    )
    assert result.name == "Test"
    assert result.value == 100


@pytest.mark.asyncio
async def test_llm_service_retry_and_fallback():
    mock_provider = MagicMock(spec=ProviderService)
    mock_provider.get_fallback_provider.return_value = "groq"

    # Primary LLM fails with timeout
    mock_primary_llm = MagicMock()
    mock_primary_struct = AsyncMock()
    mock_primary_struct.ainvoke.side_effect = TimeoutError("Simulated timeout")
    mock_primary_llm.with_structured_output.return_value = mock_primary_struct

    # Fallback LLM succeeds
    mock_fallback_llm = MagicMock()
    mock_fallback_struct = AsyncMock()
    mock_fallback_struct.ainvoke.return_value = DummySchema(name="Fallback", value=42)
    mock_fallback_llm.with_structured_output.return_value = mock_fallback_struct

    def get_llm_side_effect(provider=None, model=None):
        if provider == "gemini":
            return mock_primary_llm
        return mock_fallback_llm

    mock_provider.get_llm.side_effect = get_llm_side_effect

    settings = Settings(
        AI_PROVIDER="gemini",
        ENABLE_PROVIDER_FALLBACK=True,
        AI_MAX_RETRIES=1,
        AI_REQUEST_TIMEOUT=1,
    )
    service = LLMService(provider_service=mock_provider, settings=settings)

    result = await service.generate_structured(
        schema=DummySchema,
        prompt="Test Prompt",
        provider="gemini",
    )
    assert result.name == "Fallback"
    assert result.value == 42
