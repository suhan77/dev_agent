# Dev Agent

`Dev Agent`는 LangGraph 기반의 코딩 에이전트를 만들기 위한 Python CLI 프로젝트 템플릿입니다.

지금 단계에서는 기능 구현보다 `State`, `Node`, `Edge`, `Graph`, `CLI` 구조를 명확하게 잡는 데 집중합니다.

## Tech Stack

- Python
- Typer
- LangGraph

## Goal

LangGraph 프로젝트를 시작할 때 바로 확장할 수 있는 기본 골격을 제공하는 것이 목표입니다.

## Project Structure

```text
src/dev_agent/
  __main__.py
  cli.py
  graph.py
  logging_config.py
  nodes.py
  state.py
```

각 파일의 역할은 다음과 같습니다.

- `state.py`: 그래프 전체에서 공유할 상태 정의
- `nodes.py`: 각 노드 함수 정의
- `graph.py`: 노드와 엣지를 연결해 그래프 구성
- `cli.py`: 터미널에서 그래프를 실행하는 진입점
- `logging_config.py`: 한국어 로그 설정

## Basic Graph

현재 기본 그래프는 아래 순서로 동작합니다.

- `START -> prepare -> execute -> finalize -> END`

기본 상태는 아래 필드를 사용합니다.

- `request`: 입력 요청
- `status`: 현재 상태
- `result`: 처리 결과
- `logs`: 실행 로그

## Usage

이 프로젝트는 `uv`만 사용하도록 구성합니다.

그래프 실행:

```bash
uv run python -m dev_agent run "기본 그래프를 실행해줘"
```

그래프 구조 확인:

```bash
uv run python -m dev_agent show-graph
```
