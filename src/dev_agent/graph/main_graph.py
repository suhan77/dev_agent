from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from dev_agent.exceptions import GraphBuildError, GraphExecutionError
from dev_agent.nodes import finalize_node, prepare_node, understand_intent_node
from dev_agent.state import AgentState


def build_main_graph():
    """메인 기능에서 사용할 기본 그래프를 생성합니다."""
    try:
        # noinspection PyTypeChecker
        builder = StateGraph(AgentState)
        # noinspection PyTypeChecker
        builder.add_node("prepare", prepare_node)
        # noinspection PyTypeChecker
        builder.add_node("understand_intent", understand_intent_node)
        # noinspection PyTypeChecker
        builder.add_node("finalize", finalize_node)

        builder.add_edge(START, "prepare")
        builder.add_edge("prepare", "understand_intent")
        builder.add_edge("understand_intent", "finalize")
        builder.add_edge("finalize", END)

        return builder.compile()
    except Exception as error:  # pragma: no cover
        raise GraphBuildError("메인 그래프를 생성하지 못했습니다.") from error


GRAPH = build_main_graph()


def run_main_graph(request: str) -> dict[str, Any] | Any:
    """메인 그래프를 실행하고 최종 상태를 반환합니다."""
    try:
        return GRAPH.invoke(
            {
                "messages": [HumanMessage(content=request)],
                "logs": [],
            }
        )
    except Exception as error:  # pragma: no cover
        raise GraphExecutionError("메인 그래프를 실행하지 못했습니다.") from error
