from __future__ import annotations


class DevAgentError(Exception):
    """Dev Agent 전역에서 사용하는 기본 예외입니다."""


class GraphBuildError(DevAgentError):
    """그래프 생성 중 문제가 발생했을 때 사용하는 예외입니다."""


class GraphExecutionError(DevAgentError):
    """그래프 실행 중 문제가 발생했을 때 사용하는 예외입니다."""


class ConfigurationError(DevAgentError):
    """환경 변수나 설정값이 올바르지 않을 때 사용하는 예외입니다."""


class LlmRequestError(DevAgentError):
    """LLM 호출 중 문제가 발생했을 때 사용하는 예외입니다."""
