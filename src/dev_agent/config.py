from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from dev_agent.llm_config import AnthropicConfig, OllamaConfig, OpenAiConfig


class Settings(BaseSettings):
    """환경 변수에서 읽어온 애플리케이션 설정입니다."""

    model_config = SettingsConfigDict(
        env_file=None,
        extra="ignore",
    )

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    ollama_api_key: str | None = Field(default=None, alias="OLLAMA_API_KEY")
    ollama_host: str = Field(default="http://localhost:11434", alias="OLLAMA_HOST")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    anthropic_model: str = Field(default="claude-3-5-sonnet-latest", alias="ANTHROPIC_MODEL")
    ollama_model: str = Field(default="llama3:latest", alias="OLLAMA_MODEL")
    request_timeout: float = Field(default=30.0, alias="LLM_REQUEST_TIMEOUT")

    @field_validator("ollama_host")
    @classmethod
    def normalize_ollama_host(cls, value: str) -> str:
        """Ollama 호스트 끝의 슬래시를 제거합니다."""
        return value.rstrip("/")

    @property
    def openai(self) -> OpenAiConfig:
        """OpenAI 설정 객체를 반환합니다."""
        return OpenAiConfig(
            api_key=self.openai_api_key,
            default_model=self.openai_model,
        )

    @property
    def anthropic(self) -> AnthropicConfig:
        """Anthropic 설정 객체를 반환합니다."""
        return AnthropicConfig(
            api_key=self.anthropic_api_key,
            default_model=self.anthropic_model,
        )

    @property
    def ollama(self) -> OllamaConfig:
        """Ollama 설정 객체를 반환합니다."""
        return OllamaConfig(
            api_key=self.ollama_api_key,
            host=self.ollama_host,
            default_model=self.ollama_model,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """운영체제 환경 변수에서 설정값을 읽어옵니다."""
    return Settings()
