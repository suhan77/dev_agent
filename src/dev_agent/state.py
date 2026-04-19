from __future__ import annotations

import operator
from typing import Annotated

from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """메시지 상태를 기반으로 확장한 Dev Agent 상태입니다."""

    intent: str
    status: str
    logs: Annotated[list[str], operator.add]
