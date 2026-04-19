from __future__ import annotations

import operator
from typing import Annotated

from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """LangGraph 전체에서 공유하는 기본 상태입니다."""

    request: str
    intent: str
    status: str
    logs: Annotated[list[str], operator.add]
