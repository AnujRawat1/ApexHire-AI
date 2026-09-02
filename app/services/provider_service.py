import logging
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from app.config.settings import Settings, get_settings
from app.exceptions.ai_exceptions import AIProviderException

logger = logging.getLogger(__name__)


class ProviderService:
    """Factory service for creating and configuring LangChain chat model instances."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    def get_llm(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> BaseChatModel:
        """Instantiates a BaseChatModel for the specified provider (or default configured provider)."""
        target_provider = (provider or self.settings.ai_provider).lower()
        temp = temperature if temperature is not None else self.settings.ai_temperature

        if target_provider == "gemini":
            return self._create_gemini_llm(model=model, temperature=temp)
        elif target_provider == "groq":
            return self._create_groq_llm(model=model, temperature=temp)
        else:
            raise AIProviderException(
                f"Unsupported AI provider '{target_provider}'. Supported providers are: 'gemini', 'groq'.",
                provider=target_provider,
            )

    def _create_gemini_llm(
        self, model: Optional[str] = None, temperature: float = 0.2
    ) -> BaseChatModel:
        api_key = self.settings.gemini_api_key
        if not api_key:
            raise AIProviderException(
                "GEMINI_API_KEY is not configured in the environment.",
                provider="gemini",
            )
        target_model = model or self.settings.gemini_model
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            logger.info(f"Instantiating ChatGoogleGenerativeAI with model: {target_model}")
            return ChatGoogleGenerativeAI(
                model=target_model,
                google_api_key=api_key,
                temperature=temperature,
                max_output_tokens=self.settings.ai_max_output_tokens,
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatGoogleGenerativeAI: {str(e)}")
            raise AIProviderException(f"Failed to initialize Gemini provider: {str(e)}", provider="gemini")

    def _create_groq_llm(
        self, model: Optional[str] = None, temperature: float = 0.2
    ) -> BaseChatModel:
        api_key = self.settings.groq_api_key
        if not api_key:
            raise AIProviderException(
                "GROQ_API_KEY is not configured in the environment.",
                provider="groq",
            )
        target_model = model or self.settings.groq_model
        try:
            from langchain_groq import ChatGroq

            logger.info(f"Instantiating ChatGroq with model: {target_model}")
            return ChatGroq(
                model=target_model,
                groq_api_key=api_key,
                temperature=temperature,
                max_tokens=self.settings.ai_max_output_tokens,
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatGroq: {str(e)}")
            raise AIProviderException(f"Failed to initialize Groq provider: {str(e)}", provider="groq")

    def get_fallback_provider(self, current_provider: str) -> Optional[str]:
        """Returns the fallback provider if fallback is enabled and available."""
        if not self.settings.enable_provider_fallback:
            return None
        current = current_provider.lower()
        if current == "gemini" and self.settings.groq_api_key:
            return "groq"
        elif current == "groq" and self.settings.gemini_api_key:
            return "gemini"
        fallback = self.settings.ai_fallback_provider
        if fallback and fallback.lower() != current:
            return fallback.lower()
        return None
