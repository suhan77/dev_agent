from __future__ import annotations

import typer

from .exceptions import DevAgentError
from .graph import GRAPH, run_main_graph, run_test_graph
from .llm import LlmProvider, LlmRequest, create_llm_client
from .logger import configure_logger

app = typer.Typer(
    no_args_is_help=True,
    help="LangGraph 기반 개발 에이전트의 기본 CLI입니다.",
)


@app.callback()
def callback() -> None:
    """개발 에이전트 명령 모음입니다."""


@app.command()
def run(
    request: str = typer.Argument(..., help="그래프에 전달할 요청 문자열입니다."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="상세 로그를 출력합니다."),
) -> None:
    """기본 LangGraph를 실행합니다."""
    configure_logger(verbose=verbose)

    try:
        result = run_main_graph(request)
    except DevAgentError as error:
        typer.echo(f"그래프 실행 중 오류가 발생했습니다: {error}")
        raise typer.Exit(code=1) from error

    typer.echo("그래프 실행 결과")
    typer.echo(f"- 상태: {result.get('status', '알 수 없음')}")
    typer.echo(f"- 의도: {result.get('intent', '의도 없음')}")

    if result.get("logs"):
        typer.echo("- 로그:")
        for item in result["logs"]:
            typer.echo(f"  - {item}")


@app.command("run-test")
def run_test(
    request: str = typer.Argument(..., help="테스트 그래프에 전달할 요청 문자열입니다."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="상세 로그를 출력합니다."),
) -> None:
    """테스트 그래프를 실행합니다."""
    configure_logger(verbose=verbose)

    try:
        result = run_test_graph(request)
    except DevAgentError as error:
        typer.echo(f"테스트 그래프 실행 중 오류가 발생했습니다: {error}")
        raise typer.Exit(code=1) from error

    typer.echo("테스트 그래프 실행 결과")
    typer.echo(f"- 상태: {result.get('status', '알 수 없음')}")

    if result.get("logs"):
        typer.echo("- 로그:")
        for item in result["logs"]:
            typer.echo(f"  - {item}")


@app.command("run-test-chat")
def run_test_chat(
    request: str = typer.Argument(..., help="Ollama에 전달할 테스트 프롬프트입니다."),
    model: str | None = typer.Option(None, "--model", "-m", help="테스트에 사용할 Ollama 모델명입니다."),
    system_prompt: str | None = typer.Option(
        "당신은 간결하게 답하는 AI 어시스턴트입니다.",
        "--system-prompt",
        help="테스트 호출에 사용할 시스템 프롬프트입니다.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="상세 로그를 출력합니다."),
) -> None:
    """실제 Ollama LLM 호출이 정상 동작하는지 테스트합니다."""
    configure_logger(verbose=verbose)

    try:
        client = create_llm_client()
        response = client.generate(
            LlmProvider.OLLAMA,
            LlmRequest(
                prompt=request,
                system_prompt=system_prompt,
                model=model,
            ),
        )
    except DevAgentError as error:
        typer.echo(f"Ollama 테스트 호출 중 오류가 발생했습니다: {error}")
        raise typer.Exit(code=1) from error

    typer.echo("Ollama 테스트 호출 결과")
    typer.echo(f"- 제공자: {response.provider.value}")
    typer.echo(f"- 모델: {response.model}")
    typer.echo("- 응답:")
    typer.echo(response.text or "(빈 응답)")


@app.command("show-graph")
def show_graph() -> None:
    """현재 그래프 구조를 Mermaid 문자열로 출력합니다."""
    typer.echo(GRAPH.get_graph().draw_mermaid())


def main() -> None:
    app()


if __name__ == "__main__":
    main()
