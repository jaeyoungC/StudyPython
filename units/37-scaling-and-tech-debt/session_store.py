"""37단원: 세션 외부화 — 서버를 상태 없이(stateless) 만들기.

인스턴스가 둘이 되는 순간, 프로세스 메모리에 있던 것들이 문제가 됩니다: 로그인 세션, 27단원 속도 제한 버킷, 28단원 브레이커 상태,
19단원 캐시. 이 모듈은 그중 가장 먼저 부딪히는 "세션"을 메모리에서 꺼내 공유 저장소(SQLite, 나중에는 Redis)로 옮깁니다.

뼈대만 있습니다. test_unit37.py 의 뼈대를 먼저 채운 뒤 구현하세요.
"""

from __future__ import annotations

import json
import sqlite3
import time
from typing import Any, Callable, Protocol


class SessionStore(Protocol):
    """세션 id → 데이터(dict). TTL 이 지나면 없는 것으로 본다."""

    def create(self, data: dict[str, Any]) -> str: ...  # 새 세션 id (secrets.token_urlsafe)

    def get(self, session_id: str) -> dict[str, Any] | None: ...

    def delete(self, session_id: str) -> None: ...


class MemorySessionStore:
    """인스턴스 하나일 때만 맞는 구현. 두 인스턴스면 app1 에서 로그인한 사용자가 app2 에서는 로그아웃 상태다.
    테스트에서 '왜 외부화가 필요한가'를 보여 주는 대조군으로 쓴다."""

    def __init__(self, *, ttl_seconds: float = 3600.0, clock: Callable[[], float] = time.time) -> None:
        # TODO
        raise NotImplementedError

    def create(self, data: dict[str, Any]) -> str:
        # TODO
        raise NotImplementedError

    def get(self, session_id: str) -> dict[str, Any] | None:
        # TODO
        raise NotImplementedError

    def delete(self, session_id: str) -> None:
        # TODO
        raise NotImplementedError


class SqliteSessionStore:
    """여러 인스턴스가 같은 DB 파일(또는 서버)을 보면 세션이 공유된다.

    테이블 sessions(id TEXT PRIMARY KEY, data TEXT NOT NULL, expires_at REAL NOT NULL)
    data 는 json.dumps 문자열. 26단원의 SqliteIdempotencyStore 와 같은 모양이다 — 같은 모양이 반복되면 공통 부모를 생각해 볼 때.
    """

    def __init__(self, conn: sqlite3.Connection, *, ttl_seconds: float = 3600.0, clock: Callable[[], float] = time.time) -> None:
        self.conn = conn
        self.ttl_seconds = ttl_seconds
        self.clock = clock

    def init_schema(self) -> None:
        """완성되어 있습니다."""
        with self.conn:
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, data TEXT NOT NULL, expires_at REAL NOT NULL)"
            )

    def create(self, data: dict[str, Any]) -> str:
        # TODO
        raise NotImplementedError

    def get(self, session_id: str) -> dict[str, Any] | None:
        # TODO
        raise NotImplementedError

    def delete(self, session_id: str) -> None:
        # TODO
        raise NotImplementedError

    def purge_expired(self) -> int:
        """만료된 행을 지우고 개수를 돌려준다. 워커(20단원)가 주기적으로 부른다."""
        # TODO
        raise NotImplementedError
