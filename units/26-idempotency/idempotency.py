"""26단원: 멱등성(idempotency) — 같은 요청을 두 번 받아도 한 번만 실행한다.

25단원의 재시도는 "결과를 모르는 호출"을 다시 보냅니다. POST /tasks 가 그렇게 두 번 오면 할 일이 두 개 생깁니다.
해결책은 클라이언트가 요청마다 고유한 `Idempotency-Key` 를 붙이고, 서버가 그 키로 "이미 처리한 요청"의 응답을
기억해 두었다가 **다시 실행하지 않고 저장된 응답을 돌려주는** 것입니다.

구성:
- make_fingerprint:        요청 본문의 지문(fingerprint). 같은 키에 다른 본문이 오면 충돌로 판정하는 근거
- IdempotencyStore:        키 → (지문, 응답) 저장소의 계약. 메모리 구현과 SQLite 구현
- execute_idempotent:      "저장소를 보고 → 없으면 실행하고 저장 → 있으면 재생(replay)" 흐름

TODO 를 채워 `pytest units/26-idempotency` 를 통과시키세요.
"""

from __future__ import annotations

import hashlib
import sqlite3
import time
from dataclasses import dataclass
from typing import Callable, Protocol


@dataclass(frozen=True)
class StoredResponse:
    """저장해 두었다가 재생할 응답. body 는 JSON 문자열."""

    status: int
    body: str


class IdempotencyConflictError(Exception):
    """같은 키로 다른 본문이 왔다. API 계층은 422 로 바꿔 돌려준다."""

    status = 422


def make_fingerprint(method: str, path: str, body: bytes) -> str:
    """요청의 지문. sha256 16진수 문자열(64자).

    입력: f"{method.upper()}\\n{path}\\n".encode("utf-8") + body
    메서드·경로·본문 중 하나라도 다르면 지문이 달라야 한다.
    """
    # TODO
    raise NotImplementedError


class IdempotencyStore(Protocol):
    """멱등성 저장소의 계약.

    get(key)  → 저장된 (지문, 응답) 또는 None. 만료된 항목은 None 으로 취급한다.
    put(key, fingerprint, response) → 저장. 같은 키가 이미 있으면 덮어쓴다.
    """

    def get(self, key: str) -> tuple[str, StoredResponse] | None: ...

    def put(self, key: str, fingerprint: str, response: StoredResponse) -> None: ...


class MemoryIdempotencyStore:
    """dict 로 구현한 저장소. 테스트와 단일 프로세스용.

    - clock() 은 초 단위 시각(time.time 과 같은 의미)
    - put 시각 + ttl_seconds 가 지난 항목은 get 에서 None
    """

    def __init__(self, *, ttl_seconds: float = 86400.0, clock: Callable[[], float] = time.time) -> None:
        self.ttl_seconds = ttl_seconds
        self.clock = clock
        self._items: dict[str, tuple[str, StoredResponse, float]] = {}  # key → (지문, 응답, 만료 시각)

    def get(self, key: str) -> tuple[str, StoredResponse] | None:
        # TODO
        raise NotImplementedError

    def put(self, key: str, fingerprint: str, response: StoredResponse) -> None:
        # TODO
        raise NotImplementedError


class SqliteIdempotencyStore:
    """SQLite 테이블로 구현한 저장소. 프로세스가 재시작해도 남는다.

    테이블 idempotency_keys(key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL,
                           status INTEGER NOT NULL, body TEXT NOT NULL, expires_at REAL NOT NULL)
    힌트: 덮어쓰기는 INSERT OR REPLACE, 테스트는 sqlite3.connect(":memory:")
    """

    def __init__(self, conn: sqlite3.Connection, *, ttl_seconds: float = 86400.0, clock: Callable[[], float] = time.time) -> None:
        self.conn = conn
        self.ttl_seconds = ttl_seconds
        self.clock = clock

    def init_schema(self) -> None:
        """테이블이 없으면 만든다. 여러 번 불러도 안전하다(CREATE TABLE IF NOT EXISTS). 완성되어 있습니다."""
        with self.conn:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS idempotency_keys (
                       key TEXT PRIMARY KEY,
                       fingerprint TEXT NOT NULL,
                       status INTEGER NOT NULL,
                       body TEXT NOT NULL,
                       expires_at REAL NOT NULL)"""
            )

    def get(self, key: str) -> tuple[str, StoredResponse] | None:
        # TODO
        raise NotImplementedError

    def put(self, key: str, fingerprint: str, response: StoredResponse) -> None:
        # TODO
        raise NotImplementedError


def execute_idempotent(
    store: IdempotencyStore,
    key: str | None,
    fingerprint: str,
    handler: Callable[[], StoredResponse],
) -> tuple[StoredResponse, bool]:
    """멱등성 키를 적용해 handler 를 실행한다. (응답, 재생 여부) 를 돌려준다.

    - key 가 None 이면(헤더 없음) 그냥 handler() 를 실행하고 (응답, False). 아무것도 저장하지 않는다.
    - 저장소에 key 가 없으면 handler() 실행 → 저장 → (응답, False)
    - 저장소에 key 가 있고 지문이 같으면 handler 를 부르지 않고 (저장된 응답, True)
    - 저장소에 key 가 있고 지문이 다르면 IdempotencyConflictError. handler 를 부르지 않는다.
    - handler 가 예외를 던지면 아무것도 저장하지 않고 예외를 그대로 전파한다
      (다음 재시도가 다시 실행될 수 있어야 한다)
    """
    # TODO
    raise NotImplementedError
