from __future__ import annotations

import logging

from .state import AgentState

logger = logging.getLogger(__name__)


def prepare_node(state: AgentState) -> AgentState:
    """그래프 실행 전에 입력값과 초기 상태를 준비합니다."""
    request = state.get("request", "").strip()
    logger.info("준비 노드 실행: 입력값을 확인합니다.")

    if not request:
        logger.warning("입력값이 비어 있어 기본 안내 문구를 사용합니다.")
        request = "아직 요청이 입력되지 않았습니다."

    return {
        "request": request,
        "status": "준비 완료",
        "logs": ["준비 노드에서 입력값을 확인했습니다."],
    }


def execute_node(state: AgentState) -> AgentState:
    """실제 작업이 들어갈 자리를 대신하는 기본 실행 노드입니다."""
    request = state["request"]
    logger.info("실행 노드 실행: 기본 처리 결과를 생성합니다.")

    return {
        "status": "실행 완료",
        "result": f"처리할 요청: {request}",
        "logs": ["실행 노드에서 기본 처리 결과를 만들었습니다."],
    }


def finalize_node(state: AgentState) -> AgentState:
    """그래프 종료 전에 최종 상태를 정리합니다."""
    logger.info("종료 노드 실행: 그래프 실행을 마무리합니다.")

    return {
        "status": "종료 완료",
        "logs": ["종료 노드에서 그래프 실행을 마무리했습니다."],
    }
