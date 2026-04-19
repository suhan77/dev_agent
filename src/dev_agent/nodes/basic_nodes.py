from __future__ import annotations

from langchain_core.messages import HumanMessage

from dev_agent.logger import get_logger
from dev_agent.state import AgentState

logger = get_logger(__name__)


def prepare_node(state: AgentState) -> AgentState:
    """그래프 실행 전에 메시지 상태를 확인하고 초기 상태를 준비합니다."""
    request = get_latest_user_message_text(state)
    logger.info("준비 노드 실행: 메시지 입력값을 확인합니다.")

    if not request:
        logger.warning("메시지가 비어 있어 기본 안내 문구를 추가합니다.")
        return {
            "messages": [HumanMessage(content="아직 요청이 입력되지 않았습니다.")],
            "status": "준비 완료",
            "logs": ["준비 노드에서 입력 메시지를 확인했습니다."],
        }

    return {
        "status": "준비 완료",
        "logs": ["준비 노드에서 입력 메시지를 확인했습니다."],
    }


def understand_intent_node(state: AgentState) -> AgentState:
    """입력 메시지를 바탕으로 사용자의 의도를 간단히 분류합니다."""
    request = get_latest_user_message_text(state)
    logger.info("의도 파악 노드 실행: 메시지의 목적을 분석합니다.")
    intent = classify_intent(request)

    return {
        "intent": intent,
        "status": "의도 파악 완료",
        "logs": [f"의도 파악 노드에서 메시지 의도를 '{intent}'로 정리했습니다."],
    }


def finalize_node(state: AgentState) -> AgentState:
    """그래프 종료 전에 최종 상태를 정리합니다."""
    logger.info("종료 노드 실행: 그래프 실행을 마무리합니다.")

    return {
        "status": "종료 완료",
        "logs": ["종료 노드에서 그래프 실행을 마무리했습니다."],
    }


def classify_intent(request: str) -> str:
    """요청 문장을 보고 가장 가까운 작업 의도를 판별합니다."""
    normalized = request.lower()

    if any(keyword in normalized for keyword in ("기획", "요구사항", "spec", "분석", "understand")):
        return "기획 이해"
    if any(keyword in normalized for keyword in ("기능", "정의", "feature")):
        return "기능 정의"
    if any(keyword in normalized for keyword in ("화면", "ui", "ux", "screen")):
        return "화면 설계"
    if any(keyword in normalized for keyword in ("db", "database", "schema", "데이터")):
        return "데이터 설계"
    if any(keyword in normalized for keyword in ("todo", "할 일", "task")):
        return "할 일 정리"
    if any(keyword in normalized for keyword in ("코드", "구현", "개발", "build")):
        return "구현 작업"
    if any(keyword in normalized for keyword in ("테스트", "검증", "test")):
        return "테스트 작업"

    return "일반 요청"


def get_latest_user_message_text(state: AgentState) -> str:
    """상태의 마지막 사용자 메시지 내용을 문자열로 반환합니다."""
    for message in reversed(state.get("messages", [])):
        if isinstance(message, HumanMessage):
            return message.content.strip()
        message_type = getattr(message, "type", "")
        if message_type == "human":
            return str(message.content).strip()

    return ""
