from __future__ import annotations

import typer

from .graph import GRAPH, run_graph
from .logging_config import configure_logging

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
    configure_logging(verbose=verbose)
    result = run_graph(request)

    typer.echo("그래프 실행 결과")
    typer.echo(f"- 상태: {result.get('status', '알 수 없음')}")
    typer.echo(f"- 결과: {result.get('result', '결과 없음')}")

    if result.get("logs"):
        typer.echo("- 로그:")
        for item in result["logs"]:
            typer.echo(f"  - {item}")


@app.command("show-graph")
def show_graph() -> None:
    """현재 그래프 구조를 Mermaid 문자열로 출력합니다."""
    typer.echo(GRAPH.get_graph().draw_mermaid())


def main() -> None:
    app()


if __name__ == "__main__":
    main()
