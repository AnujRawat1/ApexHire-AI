from functools import lru_cache
from typing import List, Optional
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application Information
    app_name: str = Field(
        default="ApexHire AI Service",
        validation_alias=AliasChoices("APP_NAME", "app_name"),
    )
    app_env: str = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENV", "app_env"),
    )
    host: str = Field(
        default="0.0.0.0",
        validation_alias=AliasChoices("HOST", "APP_HOST", "host"),
    )
    port: int = Field(
        default=8000,
        validation_alias=AliasChoices("PORT", "APP_PORT", "port"),
    )

    # Primary LLM Provider Configuration
    ai_provider: str = Field(
        default="gemini",
        validation_alias=AliasChoices("AI_PROVIDER", "DEFAULT_LLM_PROVIDER", "ai_provider"),
    )
    ai_model: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("AI_MODEL", "ai_model"),
    )
    ai_temperature: float = Field(
        default=0.2,
        validation_alias=AliasChoices("AI_TEMPERATURE", "LLM_TEMPERATURE", "ai_temperature"),
    )
    ai_max_output_tokens: int = Field(
        default=4096,
        validation_alias=AliasChoices("AI_MAX_OUTPUT_TOKENS", "LLM_MAX_OUTPUT_TOKENS", "ai_max_output_tokens"),
    )

    # Gemini Provider Settings
    gemini_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("GEMINI_API_KEY", "gemini_api_key"),
    )
    gemini_model: str = Field(
        default="gemini-flash-latest",
        validation_alias=AliasChoices("GEMINI_MODEL", "gemini_model"),
    )

    # Groq Provider Settings
    groq_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("GROQ_API_KEY", "groq_api_key"),
    )
    groq_model: str = Field(
        default="qwen/qwen3.8-27b",
        validation_alias=AliasChoices("GROQ_MODEL", "groq_model"),
    )

    # Service-to-Service Security Key
    ai_service_api_key: str = Field(
        default="dev-api-key",
        validation_alias=AliasChoices("AI_SERVICE_API_KEY", "PYTHON_SERVICE_API_KEY", "ai_service_api_key"),
    )

    # Resilience & Fallback
    ai_request_timeout: int = Field(
        default=120,
        validation_alias=AliasChoices("AI_REQUEST_TIMEOUT", "ai_request_timeout"),
    )
    ai_max_retries: int = Field(
        default=2,
        validation_alias=AliasChoices("AI_MAX_RETRIES", "ai_max_retries"),
    )
    enable_provider_fallback: bool = Field(
        default=True,
        validation_alias=AliasChoices("ENABLE_PROVIDER_FALLBACK", "enable_provider_fallback"),
    )
    ai_fallback_provider: Optional[str] = Field(
        default="groq",
        validation_alias=AliasChoices("AI_FALLBACK_PROVIDER", "ai_fallback_provider"),
    )
    ai_fallback_model: Optional[str] = Field(
        default="llama-3.3-70b-versatile",
        validation_alias=AliasChoices("AI_FALLBACK_MODEL", "ai_fallback_model"),
    )

    # CORS & Network
    cors_origins: str = Field(
        default="http://localhost:9000,http://localhost:5173,http://localhost:3000",
        validation_alias=AliasChoices("CORS_ORIGINS", "cors_origins"),
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("LOG_LEVEL", "log_level"),
    )

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.cors_origins:
            return []
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def get_effective_model(self, provider: Optional[str] = None) -> str:
        """Returns the effective model name for the given or configured provider."""
        active_provider = (provider or self.ai_provider).lower()
        if self.ai_model and not provider:
            return self.ai_model
        if active_provider == "gemini":
            return self.gemini_model
        elif active_provider == "groq":
            return self.groq_model
        return self.ai_model or "gemini-2.0-flash"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
