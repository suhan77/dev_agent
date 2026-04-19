from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .nodes import execute_node, finalize_node, prepare_node
from .state import AgentState


def build_graph():
    """기본 LangGraph 골격을 생성합니다."""
    builder = StateGraph(AgentState)

    builder.add_node("prepare", prepare_node)
    builder.add_node("execute", execute_node)
    builder.add_node("finalize", finalize_node)

    builder.add_edge(START, "prepare")
    builder.add_edge("prepare", "execute")
    builder.add_edge("execute", "finalize")
    builder.add_edge("finalize", END)

    return builder.compile()


GRAPH = build_graph()


def run_graph(request: str) -> AgentState:
    """기본 그래프를 실행하고 최종 상태를 반환합니다."""
    return GRAPH.invoke({"request": request, "logs": []})
