"""26단원 테스트. 실행: pytest units/26-idempotency

두 저장소(메모리·SQLite)에 같은 테스트를 돌립니다(24단원의 계약 테스트). 시간은 FakeClock 으로 주입합니다.
"""

import json
import sqlite3

import pytest

from idempotency import (
    IdempotencyConflictError,
    MemoryIdempotencyStore,
    SqliteIdempotencyStore,
    StoredResponse,
    execute_idempotent,
    make_fingerprint,
)


class FakeClock:
    def __init__(self, now: float = 1_000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class CountingHandler:
    """불릴 때마다 새 id 로 201 응답을 만든다. 호출 횟수를 센다."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self) -> StoredResponse:
        self.calls += 1
        return StoredResponse(201, json.dumps({"id": self.calls, "title": "SQL 공부"}))


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture(params=["memory", "sqlite"])
def store(request, clock):
    if request.param == "memory":
        return MemoryIdempotencyStore(ttl_seconds=60.0, clock=clock)
    conn = sqlite3.connect(":memory:")
    s = SqliteIdempotencyStore(conn, ttl_seconds=60.0, clock=clock)
    s.init_schema()
    return s


FP = make_fingerprint  # 줄여 쓰기


# ---------------------------------------------------------------------------
# 지문
# ---------------------------------------------------------------------------


def test_fingerprint_is_stable_for_same_request():
    a = FP("POST", "/tasks", b'{"title": "a"}')
    b = FP("post", "/tasks", b'{"title": "a"}')  # 메서드는 대소문자 무시
    assert a == b
    assert len(a) == 64 and all(c in "0123456789abcdef" for c in a)


@pytest.mark.parametrize(
    "other",
    [
        ("POST", "/tasks", b'{"title": "b"}'),  # 본문이 다르다
        ("PUT", "/tasks", b'{"title": "a"}'),  # 메서드가 다르다
        ("POST", "/tasks/1/complete", b'{"title": "a"}'),  # 경로가 다르다
    ],
)
def test_fingerprint_changes_when_request_changes(other):
    assert FP("POST", "/tasks", b'{"title": "a"}') != FP(*other)


# ---------------------------------------------------------------------------
# 저장소 계약
# ---------------------------------------------------------------------------


def test_store_get_missing_key_returns_none(store):
    assert store.get("k1") is None


def test_store_put_then_get(store):
    store.put("k1", "fp1", StoredResponse(201, '{"id": 1}'))
    assert store.get("k1") == ("fp1", StoredResponse(201, '{"id": 1}'))


def test_store_put_overwrites_same_key(store):
    store.put("k1", "fp1", StoredResponse(201, "a"))
    store.put("k1", "fp2", StoredResponse(200, "b"))
    assert store.get("k1") == ("fp2", StoredResponse(200, "b"))


def test_store_entry_expires_after_ttl(store, clock):
    store.put("k1", "fp1", StoredResponse(201, "a"))
    clock.advance(59.0)
    assert store.get("k1") is not None
    clock.advance(2.0)
    assert store.get("k1") is None


def test_sqlite_init_schema_is_repeatable_and_data_survives_new_instance(clock):
    conn = sqlite3.connect(":memory:")
    first = SqliteIdempotencyStore(conn, clock=clock)
    first.init_schema()
    first.put("k1", "fp1", StoredResponse(201, "a"))

    second = SqliteIdempotencyStore(conn, clock=clock)
    second.init_schema()  # 두 번째 호출이 기존 데이터를 지우면 안 된다
    assert second.get("k1") == ("fp1", StoredResponse(201, "a"))


# ---------------------------------------------------------------------------
# execute_idempotent
# ---------------------------------------------------------------------------


def test_first_request_runs_handler_and_stores(store):
    handler = CountingHandler()
    fp = FP("POST", "/tasks", b"{}")

    response, replayed = execute_idempotent(store, "k1", fp, handler)

    assert replayed is False
    assert response.status == 201
    assert handler.calls == 1
    assert store.get("k1") == (fp, response)


def test_same_request_twice_replays_without_running_handler(store):
    handler = CountingHandler()
    fp = FP("POST", "/tasks", b"{}")

    first, _ = execute_idempotent(store, "k1", fp, handler)
    second, replayed = execute_idempotent(store, "k1", fp, handler)

    assert replayed is True
    assert second == first  # id 가 1 인 같은 응답. 할 일이 두 개 생기지 않았다
    assert handler.calls == 1


def test_same_key_with_different_body_is_a_conflict(store):
    handler = CountingHandler()
    execute_idempotent(store, "k1", FP("POST", "/tasks", b'{"title": "a"}'), handler)

    with pytest.raises(IdempotencyConflictError) as info:
        execute_idempotent(store, "k1", FP("POST", "/tasks", b'{"title": "b"}'), handler)

    assert info.value.status == 422
    assert handler.calls == 1  # 충돌한 요청은 실행되지 않았다


def test_different_keys_are_independent(store):
    handler = CountingHandler()
    fp = FP("POST", "/tasks", b"{}")

    a, _ = execute_idempotent(store, "k1", fp, handler)
    b, _ = execute_idempotent(store, "k2", fp, handler)

    assert handler.calls == 2
    assert a != b


def test_missing_key_runs_every_time_and_stores_nothing(store):
    handler = CountingHandler()
    fp = FP("POST", "/tasks", b"{}")

    _, replayed1 = execute_idempotent(store, None, fp, handler)
    _, replayed2 = execute_idempotent(store, None, fp, handler)

    assert (replayed1, replayed2) == (False, False)
    assert handler.calls == 2


def test_expired_key_runs_handler_again(store, clock):
    handler = CountingHandler()
    fp = FP("POST", "/tasks", b"{}")

    execute_idempotent(store, "k1", fp, handler)
    clock.advance(61.0)
    _, replayed = execute_idempotent(store, "k1", fp, handler)

    assert replayed is False
    assert handler.calls == 2


def test_handler_failure_stores_nothing_so_retry_can_run(store):
    fp = FP("POST", "/tasks", b"{}")
    calls = {"n": 0}

    def flaky() -> StoredResponse:
        calls["n"] += 1
        if calls["n"] == 1:
            raise ConnectionError("DB 잠김")
        return StoredResponse(201, '{"id": 1}')

    with pytest.raises(ConnectionError):
        execute_idempotent(store, "k1", fp, flaky)
    assert store.get("k1") is None

    response, replayed = execute_idempotent(store, "k1", fp, flaky)
    assert (response.status, replayed) == (201, False)
    assert calls["n"] == 2


def test_stored_error_responses_are_replayed_too(store):
    """4xx 도 '처리 결과'다. 같은 요청을 다시 보내면 같은 422 를 받아야 한다."""
    fp = FP("POST", "/tasks", b'{"title": ""}')
    handler = CountingHandler()

    def rejects() -> StoredResponse:
        handler.calls += 1
        return StoredResponse(422, '{"error": {"code": "empty_title", "message": "빈 제목"}}')

    first, _ = execute_idempotent(store, "k1", fp, rejects)
    second, replayed = execute_idempotent(store, "k1", fp, rejects)
    assert (first.status, second, replayed) == (422, first, True)
    assert handler.calls == 1
