from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama

from dev_agent.config import AnthropicConfig, OllamaConfig, OpenAiConfig, get_settings
from dev_agent.llm import (
    LangChainLlmClient,
    LlmProvider,
    LlmRequest,
    create_anthropic_chat_model,
    create_llm_client,
    create_ollama_chat_model,
    create_openai_chat_model,
    get_provider_config,
    infer_provider_from_model,
)


def test_get_settings_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    monkeypatch.setenv("OLLAMA_API_KEY", "ollama-key")
    monkeypatch.setenv("OLLAMA_HOST", "http://ollama.local:11434/")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-test")
    monkeypatch.setenv("OLLAMA_MODEL", "llama-test")
    monkeypatch.setenv("LLM_REQUEST_TIMEOUT", "12")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.openai_api_key == "openai-key"
    assert settings.anthropic_api_key == "anthropic-key"
    assert settings.ollama_api_key == "ollama-key"
    assert settings.ollama_host == "http://ollama.local:11434"
    assert settings.openai_model == "gpt-test"
    assert settings.anthropic_model == "claude-test"
    assert settings.ollama_model == "llama-test"
    assert settings.request_timeout == 12.0


def test_create_openai_chat_model(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")
    get_settings.cache_clear()
    settings = get_settings()
    config = settings.openai

    chat_model = create_openai_chat_model(config, "gpt-4.1-mini", LlmRequest(prompt="테스트"))

    assert isinstance(chat_model, ChatOpenAI)
    assert chat_model.model_name == "gpt-4.1-mini"


def test_generate_builds_langchain_messages(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-test")
    get_settings.cache_clear()
    captured_messages: list[object] = []

    class FakeChatModel:
        def invoke(self, messages):
            captured_messages.extend(messages)
            return AIMessage(content="의도는 기획 이해입니다.")
    client = LangChainLlmClient(settings=get_settings())
    client.create_chat_model = lambda model_name, request: FakeChatModel()
    response = client.generate(
        LlmRequest(
            prompt="기획 내용을 분석해줘",
            system_prompt="요청 의도를 파악해줘",
            model="claude-3-5-sonnet-latest",
        ),
    )

    assert isinstance(captured_messages[0], SystemMessage)
    assert isinstance(captured_messages[1], HumanMessage)
    assert response.provider is LlmProvider.CLAUDE
    assert response.text == "의도는 기획 이해입니다."


def test_create_ollama_chat_model(monkeypatch) -> None:
    monkeypatch.setenv("OLLAMA_HOST", "http://ollama.local:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen3")
    get_settings.cache_clear()
    settings = get_settings()
    config = settings.ollama

    chat_model = create_ollama_chat_model(
        config,
        "qwen3",
        LlmRequest(prompt="테스트 프롬프트", model="qwen3", temperature=0.2, max_tokens=256),
    )

    assert isinstance(chat_model, ChatOllama)
    assert chat_model.model == "qwen3"
    assert chat_model.base_url == "http://ollama.local:11434"


def test_create_anthropic_chat_model(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
    get_settings.cache_clear()
    settings = get_settings()
    config = settings.anthropic

    chat_model = create_anthropic_chat_model(
        config,
        "claude-3-5-sonnet-latest",
        LlmRequest(prompt="테스트 프롬프트"),
    )

    assert isinstance(chat_model, ChatAnthropic)
    assert chat_model.model == "claude-3-5-sonnet-latest"


def test_create_llm_client_returns_langchain_client() -> None:
    client = create_llm_client()

    assert isinstance(client, LangChainLlmClient)


def test_infer_provider_from_model_name() -> None:
    assert infer_provider_from_model("gpt-4.1-mini") is LlmProvider.CHATGPT
    assert infer_provider_from_model("claude-3-5-sonnet-latest") is LlmProvider.CLAUDE
    assert infer_provider_from_model("qwen3.5:latest") is LlmProvider.OLLAMA


def test_get_provider_config_returns_separated_config_models(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    monkeypatch.setenv("OLLAMA_HOST", "http://ollama.local:11434")
    get_settings.cache_clear()
    settings = get_settings()

    assert isinstance(get_provider_config(LlmProvider.CHATGPT, settings), OpenAiConfig)
    assert isinstance(get_provider_config(LlmProvider.CLAUDE, settings), AnthropicConfig)
    assert isinstance(get_provider_config(LlmProvider.OLLAMA, settings), OllamaConfig)
