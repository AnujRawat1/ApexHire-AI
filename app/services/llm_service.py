import asyncio
import logging
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.config.settings import Settings, get_settings
from app.exceptions.ai_exceptions import (
    AIProviderException,
    AIProviderRateLimitException,
    AIProviderTimeoutException,
    AIResponseValidationException,
)
from app.services.provider_service import ProviderService

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMService:
    """Service layer abstracting LLM invocations, structured output, retries, and provider fallbacks."""

    def __init__(
        self,
        provider_service: Optional[ProviderService] = None,
        settings: Optional[Settings] = None,
    ):
        self.settings = settings or get_settings()
        self.provider_service = provider_service or ProviderService(self.settings)

    async def generate_structured(
        self,
        schema: Type[T],
        prompt: str,
        system_instruction: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> T:
        """Executes an LLM call with structured output schema, with automatic retry and provider fallback."""
        primary_provider = (provider or self.settings.ai_provider).lower()

        try:
            return await self._execute_with_retry(
                schema=schema,
                prompt=prompt,
                system_instruction=system_instruction,
                provider=primary_provider,
                model=model,
            )
        except (AIProviderException, AIProviderTimeoutException, AIProviderRateLimitException) as exc:
            fallback_provider = self.provider_service.get_fallback_provider(primary_provider)
            if fallback_provider and fallback_provider != primary_provider:
                logger.warning(
                    f"Primary provider '{primary_provider}' failed with: {exc.message}. "
                    f"Attempting fallback to provider '{fallback_provider}'."
                )
                try:
                    fallback_model = (
                        self.settings.ai_fallback_model
                        if fallback_provider == self.settings.ai_fallback_provider
                        else (self.settings.gemini_model if fallback_provider == "gemini" else self.settings.groq_model)
                    )
                    return await self._execute_with_retry(
                        schema=schema,
                        prompt=prompt,
                        system_instruction=system_instruction,
                        provider=fallback_provider,
                        model=fallback_model,
                    )
                except Exception as fallback_exc:
                    logger.error(f"Fallback provider '{fallback_provider}' also failed: {str(fallback_exc)}")
                    raise exc from fallback_exc
            raise exc

    async def _execute_with_retry(
        self,
        schema: Type[T],
        prompt: str,
        system_instruction: Optional[str] = None,
        provider: str = "gemini",
        model: Optional[str] = None,
    ) -> T:
        max_retries = self.settings.ai_max_retries
        base_delay = 0.5

        for attempt in range(max_retries + 1):
            try:
                return await self._invoke_structured(
                    schema=schema,
                    prompt=prompt,
                    system_instruction=system_instruction,
                    provider=provider,
                    model=model,
                )
            except (AIProviderTimeoutException, AIProviderRateLimitException) as e:
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Transient error on provider '{provider}' (attempt {attempt + 1}/{max_retries + 1}): {e.message}. Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    raise e
            except AIResponseValidationException as e:
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Structured response validation failed (attempt {attempt + 1}/{max_retries + 1}): {e.message}. Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    raise e
            except Exception as e:
                # Classify exception
                classified = self._classify_exception(e, provider)
                if isinstance(classified, (AIProviderTimeoutException, AIProviderRateLimitException)) and attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Retryable error on provider '{provider}' (attempt {attempt + 1}/{max_retries + 1}): {classified.message}. Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    raise classified

        raise AIProviderException("Exhausted retries without a successful response.", provider=provider)

    async def _invoke_structured(
        self,
        schema: Type[T],
        prompt: str,
        system_instruction: Optional[str] = None,
        provider: str = "gemini",
        model: Optional[str] = None,
    ) -> T:
        llm = self.provider_service.get_llm(provider=provider, model=model)
        structured_llm = llm.with_structured_output(schema)

        messages = []
        if system_instruction:
            messages.append(SystemMessage(content=system_instruction))
        messages.append(HumanMessage(content=prompt))

        call_timeout = min(30.0, float(self.settings.ai_request_timeout))
        try:
            response = await asyncio.wait_for(
                structured_llm.ainvoke(messages),
                timeout=call_timeout,
            )

            if response is None:
                raise AIResponseValidationException("LLM structured output returned None.")

            if isinstance(response, schema):
                return response
            elif isinstance(response, dict):
                return schema.model_validate(response)
            else:
                return schema.model_validate(response)

        except asyncio.TimeoutError:
            raise AIProviderTimeoutException(
                f"Analysis timed out after {call_timeout}s.",
                provider=provider,
            )
        except Exception as e:
            if isinstance(e, (AIProviderTimeoutException, AIProviderRateLimitException, AIResponseValidationException)):
                raise e
            raise self._classify_exception(e, provider)

    def _classify_exception(self, e: Exception, provider: str) -> Exception:
        msg = str(e).lower()
        if "timeout" in msg or "timed out" in msg or "deadline" in msg:
            return AIProviderTimeoutException(f"Upstream provider timeout: {str(e)}", provider=provider)
        if "rate limit" in msg or "429" in msg or "quota" in msg or "resource_exhausted" in msg:
            return AIProviderRateLimitException(f"Upstream rate limit exceeded: {str(e)}", provider=provider)
        if "validation" in msg or "pydantic" in msg or "parse" in msg or "json" in msg:
            return AIResponseValidationException(f"Failed to parse LLM structured output: {str(e)}")
        return AIProviderException(f"LLM execution error: {str(e)}", provider=provider)
