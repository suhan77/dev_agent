from __future__ import annotations

from pydantic import BaseModel


class OpenAiConfig(BaseModel):
    """OpenAI 계열 모델 설정입니다."""

    api_key: str | None = None
    default_model: str = "gpt-4.1-mini"


class AnthropicConfig(BaseModel):
    """Anthropic 계열 모델 설정입니다."""

    api_key: str | None = None
    default_model: str = "claude-3-5-sonnet-latest"


class OllamaConfig(BaseModel):
    """Ollama 계열 모델 설정입니다."""

    api_key: str | None = None
    host: str = "http://localhost:11434"
    default_model: str = "llama3:latest"
