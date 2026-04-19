from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from dev_agent.exceptions import GraphBuildError, GraphExecutionError
from dev_agent.nodes import finalize_node, prepare_node
from dev_agent.state import AgentState


def build_test_graph():
    """테스트 용도로 사용할 단순 그래프를 생성합니다."""
    try:
        builder = StateGraph(AgentState)

        builder.add_node("prepare", prepare_node)
        builder.add_node("finalize", finalize_node)

        builder.add_edge(START, "prepare")
        builder.add_edge("prepare", "finalize")
        builder.add_edge("finalize", END)

        return builder.compile()
    except Exception as error:  # pragma: no cover
        raise GraphBuildError("테스트 그래프를 생성하지 못했습니다.") from error


TEST_GRAPH = build_test_graph()


def run_test_graph(request: str) -> AgentState:
    """테스트 그래프를 실행하고 최종 상태를 반환합니다."""
    try:
        return TEST_GRAPH.invoke({"request": request, "logs": []})
    except Exception as error:  # pragma: no cover
        raise GraphExecutionError("테스트 그래프를 실행하지 못했습니다.") from error
