"""37단원 테스트 뼈대. 실행: pytest units/37-scaling-and-tech-debt

핵심 실험: "인스턴스 두 개"를 저장소 객체 두 개로 흉내 낸다. 메모리 저장소 둘은 서로 모르지만, 같은 커넥션을 보는 SQLite 저장소 둘은 공유한다.
"""

import sqlite3

import pytest

from session_store import MemorySessionStore, SqliteSessionStore


class FakeClock:
    def __init__(self, now: float = 1_000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def shared_conn():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


def test_memory_store_create_get_delete(clock):
    """create 가 돌려준 id 로 get 하면 같은 dict(복사본이어도 됨), delete 뒤에는 None."""
    pytest.fail("아직 구현하지 않음")


def test_session_ids_are_unpredictable_and_unique():
    """100개 만들면 모두 다르고 길이가 32 이상이다 (secrets.token_urlsafe)."""
    pytest.fail("아직 구현하지 않음")


def test_session_expires_after_ttl(clock):
    """ttl_seconds=60 에서 61초 뒤 get 은 None (두 저장소 모두, parametrize 로)."""
    pytest.fail("아직 구현하지 않음")


def test_two_memory_instances_do_not_share_sessions(clock):
    """app1 = MemorySessionStore(), app2 = MemorySessionStore(). app1.create 한 id 를 app2.get 하면 None.
    → 로드 밸런서가 다음 요청을 app2 로 보내면 사용자는 로그아웃된다. 이것이 외부화의 이유다."""
    pytest.fail("아직 구현하지 않음")


def test_two_sqlite_instances_share_sessions(shared_conn, clock):
    """같은 커넥션(=같은 DB)을 보는 SqliteSessionStore 두 개: app1.create 한 id 를 app2.get 하면 같은 데이터."""
    pytest.fail("아직 구현하지 않음")


def test_sqlite_delete_on_one_instance_is_visible_on_other(shared_conn, clock):
    """app2.delete 뒤 app1.get 도 None (로그아웃이 모든 인스턴스에 반영)."""
    pytest.fail("아직 구현하지 않음")


def test_sqlite_data_round_trips_through_json(shared_conn, clock):
    """{"user_id": 7, "roles": ["admin"], "flags": {"beta": True}} 가 그대로 돌아온다."""
    pytest.fail("아직 구현하지 않음")


def test_purge_expired_removes_only_expired_rows(shared_conn, clock):
    """세션 3개 중 2개를 만료시키고 purge_expired() 가 2 를 돌려주며 남은 1개는 get 된다."""
    pytest.fail("아직 구현하지 않음")


def test_unknown_session_id_returns_none(shared_conn, clock):
    """없는 id 는 예외가 아니라 None."""
    pytest.fail("아직 구현하지 않음")
