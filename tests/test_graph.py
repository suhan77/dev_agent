from dev_agent.graph import (
    build_main_graph,
    build_test_graph,
    run_main_graph,
    run_test_graph,
)


def test_run_main_graph_returns_intent_state() -> None:
    result = run_main_graph("기획 내용을 분석해줘")

    assert result["status"] == "종료 완료"
    assert result["intent"] == "기획 이해"
    assert len(result["logs"]) == 3


def test_main_graph_contains_expected_nodes() -> None:
    graph = build_main_graph()
    mermaid = graph.get_graph().draw_mermaid()

    assert "prepare" in mermaid
    assert "understand_intent" in mermaid
    assert "finalize" in mermaid


def test_run_test_graph_skips_intent_node() -> None:
    result = run_test_graph("테스트 그래프를 확인해줘")

    assert result["status"] == "종료 완료"
    assert "intent" not in result
    assert len(result["logs"]) == 2


def test_test_graph_contains_only_prepare_and_finalize() -> None:
    graph = build_test_graph()
    mermaid = graph.get_graph().draw_mermaid()

    assert "prepare" in mermaid
    assert "finalize" in mermaid
    assert "understand_intent" not in mermaid
