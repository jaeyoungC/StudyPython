"""14단원: 감사 로그(audit log) — "누가, 언제, 무엇을, 어느 할 일에" 를 추가만 하는 테이블에 남긴다.

삭제·완료·검색처럼 되돌리기 어렵거나 민감한 동작을 기록한다. 에이전트가 운영 데이터를 만지기 시작하면(43단원)
"어제 누가 이 할 일을 지웠지?" 에 답할 수 있는 유일한 자료다. 시각은 주입된 시계에서 얻는다.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any, Callable


class AuditLog:
    def __init__(self, conn: sqlite3.Connection, clock: Callable[[], datetime] = datetime.now) -> None:
        self.conn = conn
        self.clock = clock

    def record(self, action: str, actor: str, task_id: int | None = None, detail: str | None = None) -> None:
        """audit_log 에 한 줄 추가. action 예: "add", "complete", "remove", "purge", "search". actor 예: "cli", "agent:planner"."""
        # TODO
        raise NotImplementedError

    def entries(self, task_id: int | None = None) -> list[dict[str, Any]]:
        """기록을 오래된 순으로. task_id 를 주면 그 할 일 것만. 각 항목은 {"at", "actor", "action", "task_id", "detail"}."""
        # TODO
        raise NotImplementedError
