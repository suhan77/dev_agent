from __future__ import annotations

from enum import Enum
from typing import Any, Protocol

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from dev_agent.config import Settings, get_settings
from dev_agent.exceptions import ConfigurationError, LlmRequestError
from dev_agent.llm_config import AnthropicConfig, OllamaConfig, OpenAiConfig


class LlmProvider(str, Enum):
    """지원하는 LLM 제공자 목록입니다."""

    OLLAMA = "ollama"
    CHATGPT = "chatgpt"
    CLAUDE = "claude"


class LlmRequest(BaseModel):
    """LLM 호출에 필요한 기본 입력값입니다."""

    prompt: str
    system_prompt: str | None = None
    model: str | None = None
    temperature: float = 0.0
    max_tokens: int | None = None


class LlmResponse(BaseModel):
    """LLM 호출 결과를 담는 공통 응답 형식입니다."""

    provider: LlmProvider
    model: str
    text: str
    raw: dict[str, Any]


class LlmClient(Protocol):
    """모든 LLM 클라이언트가 따라야 하는 공통 인터페이스입니다."""

    def create_chat_model(self, model_name: str, request: LlmRequest) -> Any:
        """모델 이름에 맞는 LangChain chat model을 생성합니다."""

    def generate(self, request: LlmRequest) -> LlmResponse:
        """단일 프롬프트를 전달하고 텍스트 응답을 반환합니다."""


class LangChainLlmClient:
    """모델 이름을 보고 적절한 LangChain chat model을 호출합니다."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings if settings is not None else get_settings()

    def create_chat_model(self, model_name: str, request: LlmRequest) -> Any:
        """모델 이름에 맞는 LangChain chat model을 생성합니다."""
        provider = infer_provider_from_model(model_name)
        config = get_provider_config(provider, self.settings)
        validate_provider_config(provider, config)

        if provider is LlmProvider.CHATGPT:
            return create_openai_chat_model(config, model_name, request)
        if provider is LlmProvider.CLAUDE:
            return create_anthropic_chat_model(config, model_name, request)
        if provider is LlmProvider.OLLAMA:
            return create_ollama_chat_model(config, model_name, request)
        raise ConfigurationError(f"지원하지 않는 LLM 제공자입니다: {provider}")

    def generate(self, request: LlmRequest) -> LlmResponse:
        """모델 이름을 기준으로 LLM을 실행하고 공통 응답 형식으로 반환합니다."""
        model_name = resolve_model_name(request, self.settings)
        provider = infer_provider_from_model(model_name)
        chat_model = self.create_chat_model(model_name, request)
        messages = build_messages(request)

        try:
            response = chat_model.invoke(messages)
        except Exception as error:  # pragma: no cover
            raise LlmRequestError("LangChain LLM 호출에 실패했습니다.") from error

        if not isinstance(response, AIMessage):
            raise LlmRequestError("LLM 응답이 AIMessage 형식이 아닙니다.")

        return LlmResponse(
            provider=provider,
            model=model_name,
            text=extract_ai_message_text(response),
            raw={
                "content": response.content,
                "response_metadata": getattr(response, "response_metadata", {}),
                "usage_metadata": getattr(response, "usage_metadata", None),
            },
        )


def create_llm_client(settings: Settings | None = None) -> LlmClient:
    """LangChain 기반 LLM 클라이언트를 생성합니다."""
    return LangChainLlmClient(settings=settings)


def resolve_model_name(request: LlmRequest, settings: Settings) -> str:
    """요청에 모델이 없으면 기본 Ollama 모델을 사용합니다."""
    return request.model or settings.ollama.default_model


def infer_provider_from_model(model_name: str) -> LlmProvider:
    """모델 이름을 보고 사용할 제공자를 추론합니다."""
    normalized = model_name.strip().lower()

    if normalized.startswith(("gpt-", "chatgpt", "o1", "o3", "o4")):
        return LlmProvider.CHATGPT
    if normalized.startswith("claude-"):
        return LlmProvider.CLAUDE
    return LlmProvider.OLLAMA


def get_provider_config(
    provider: LlmProvider,
    settings: Settings,
) -> OpenAiConfig | AnthropicConfig | OllamaConfig:
    """제공자에 맞는 설정 객체를 반환합니다."""
    if provider is LlmProvider.CHATGPT:
        return settings.openai
    if provider is LlmProvider.CLAUDE:
        return settings.anthropic
    if provider is LlmProvider.OLLAMA:
        return settings.ollama
    raise ConfigurationError(f"지원하지 않는 LLM 제공자입니다: {provider}")


def validate_provider_config(
    provider: LlmProvider,
    config: OpenAiConfig | AnthropicConfig | OllamaConfig,
) -> None:
    """필수 설정이 있는지 확인합니다."""
    if provider is LlmProvider.CHATGPT and not config.api_key:
        raise ConfigurationError("OPENAI_API_KEY 환경 변수가 필요합니다.")
    if provider is LlmProvider.CLAUDE and not config.api_key:
        raise ConfigurationError("ANTHROPIC_API_KEY 환경 변수가 필요합니다.")


def create_openai_chat_model(
    config: OpenAiConfig,
    model_name: str,
    request: LlmRequest,
) -> ChatOpenAI:
    """OpenAI 전용 LangChain chat model을 생성합니다."""
    kwargs: dict[str, Any] = {
        "model": model_name,
        "api_key": config.api_key,
        "temperature": request.temperature,
    }
    if request.max_tokens is not None:
        kwargs["max_tokens"] = request.max_tokens
    return ChatOpenAI(**kwargs)


def create_anthropic_chat_model(
    config: AnthropicConfig,
    model_name: str,
    request: LlmRequest,
) -> ChatAnthropic:
    """Anthropic 전용 LangChain chat model을 생성합니다."""
    kwargs: dict[str, Any] = {
        "model": model_name,
        "api_key": config.api_key,
        "temperature": request.temperature,
    }
    if request.max_tokens is not None:
        kwargs["max_tokens"] = request.max_tokens
    return ChatAnthropic(**kwargs)


def create_ollama_chat_model(
    config: OllamaConfig,
    model_name: str,
    request: LlmRequest,
) -> ChatOllama:
    """Ollama 전용 LangChain chat model을 생성합니다."""
    kwargs: dict[str, Any] = {
        "model": model_name,
        "base_url": config.host,
        "temperature": request.temperature,
    }
    if request.max_tokens is not None:
        kwargs["num_predict"] = request.max_tokens
    return ChatOllama(**kwargs)


def build_messages(request: LlmRequest) -> list[BaseMessage]:
    """LLM 호출용 LangChain 메시지 목록을 생성합니다."""
    messages: list[BaseMessage] = []
    if request.system_prompt:
        messages.append(SystemMessage(content=request.system_prompt))
    messages.append(HumanMessage(content=request.prompt))
    return messages


def extract_ai_message_text(message: AIMessage) -> str:
    """LangChain AIMessage에서 사람이 읽을 텍스트를 꺼냅니다."""
    if isinstance(message.content, str):
        return message.content.strip()

    texts: list[str] = []
    for item in message.content:
        if isinstance(item, str):
            texts.append(item)
            continue
        if isinstance(item, dict) and "text" in item:
            texts.append(str(item["text"]))

    return "\n".join(texts).strip()
