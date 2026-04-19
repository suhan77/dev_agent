from dev_agent.graph import build_graph, run_graph


def test_run_graph_returns_basic_state() -> None:
    result = run_graph("LangGraph 기본 구조를 확인한다.")

    assert result["status"] == "종료 완료"
    assert "LangGraph 기본 구조" in result["result"]
    assert len(result["logs"]) == 3


def test_graph_contains_expected_nodes() -> None:
    graph = build_graph()
    mermaid = graph.get_graph().draw_mermaid()

    assert "prepare" in mermaid
    assert "execute" in mermaid
    assert "finalize" in mermaid
