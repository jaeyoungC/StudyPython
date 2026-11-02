"""13단원 테스트. 실행: pytest units/13-storage-types

앞부분은 **같은 테스트를 두 저장소(관계형·문서형)에 돌린다.** 픽스처의 params 가 저장소를 바꿔 가며
각 테스트를 두 번 실행한다. 같은 동작을 두 구조가 어떻게 다르게 구현하는지가 이 단원의 질문이다.
"""

import json
import sqlite3
from datetime import date

import pytest

from todo import Task, TaskNotFoundError
from todo.cache_kv import TtlCache
from todo.migrate import current_version
from todo.storage_document import DocumentTaskStore
from todo.storage_sqlite import SqliteTaskStore


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture(params=["relational", "document"])
def store(request, conn):
    cls = SqliteTaskStore if request.param == "relational" else DocumentTaskStore
    s = cls(conn)
    s.init_schema()
    return s


# --- 같은 기능, 두 구조 -------------------------------------------------------------------


def test_add_and_get(store):
    task = store.add("a", tags=["y", "x"], due=date(2026, 2, 1))
    assert task == Task(id=1, title="a", tags=["x", "y"], due=date(2026, 2, 1))
    assert store.get(1) == task


def test_add_rejects_empty_title(store):
    with pytest.raises(ValueError):
        store.add("   ")
    assert len(store) == 0


def test_get_missing_raises(store):
    with pytest.raises(TaskNotFoundError):
        store.get(5)


def test_complete_and_open_tasks(store):
    store.add("a")
    store.add("b")
    assert store.complete(1).done is True
    assert store.get(1).version == 2
    assert [t.id for t in store.open_tasks()] == [2]
    with pytest.raises(ValueError):
        store.complete(1)


def test_remove(store):
    store.add("a")
    store.add("b")
    assert store.remove(1).title == "a"
    assert [t.id for t in store.all()] == [2]
    assert store.add("c").id == 3


def test_by_tag(store):
    store.add("a", tags=["공부"])
    store.add("b", tags=["운동"])
    store.add("c", tags=["공부", "운동"])
    assert [t.id for t in store.by_tag("공부")] == [1, 3]
    assert store.by_tag("없음") == []


def test_tag_counts(store):
    store.add("a", tags=["공부"])
    store.add("b", tags=["공부", "운동"])
    assert store.tag_counts() == {"공부": 2, "운동": 1}


# --- 문서형만의 성질 ------------------------------------------------------------------------


def test_document_store_keeps_whole_task_in_one_json_body(conn):
    store = DocumentTaskStore(conn)
    store.init_schema()
    store.add("a", tags=["x"], due=date(2026, 1, 1))
    (body,) = conn.execute("SELECT body FROM task_documents WHERE id = 1").fetchone()
    assert json.loads(body) == {"title": "a", "done": False, "tags": ["x"], "version": 1, "due": "2026-01-01"}


def test_document_store_uses_a_single_table(conn):
    DocumentTaskStore(conn).init_schema()
    names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert names == {"task_documents"}


def test_document_store_rejects_invalid_json(conn):
    DocumentTaskStore(conn).init_schema()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO task_documents (body) VALUES ('{not json')")


def test_document_store_accepts_fields_relational_schema_does_not_know(conn):
    """스키마가 없다는 것의 양면: 아무 키나 넣을 수 있다. 읽는 쪽(Task)이 모르는 키면 어떻게 되는가?"""
    DocumentTaskStore(conn).init_schema()
    conn.execute(
        "INSERT INTO task_documents (body) VALUES (?)",
        (json.dumps({"title": "a", "done": False, "tags": [], "version": 1, "due": None, "color": "red"}),),
    )
    with pytest.raises(TypeError):  # Task 에 color 필드가 없다 — 문서형에서는 이런 오류가 '읽을 때' 터진다
        DocumentTaskStore(conn).get(1)


# --- 키-값 + TTL ---------------------------------------------------------------------------


class FakeClock:
    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def cache(clock):
    return TtlCache(clock=clock)


def test_cache_returns_value_before_expiry(cache, clock):
    cache.set("tag_counts", {"공부": 2}, ttl_seconds=60)
    clock.now = 59.9
    assert cache.get("tag_counts") == {"공부": 2}
    assert "tag_counts" in cache


def test_cache_expires_at_ttl(cache, clock):
    cache.set("k", 1, ttl_seconds=60)
    clock.now = 60
    assert cache.get("k") is None
    assert cache.get("k", "기본값") == "기본값"
    assert "k" not in cache


def test_cache_missing_key_returns_default(cache):
    assert cache.get("없음") is None
    assert cache.get("없음", 0) == 0


def test_cache_set_overwrites_and_resets_ttl(cache, clock):
    cache.set("k", 1, ttl_seconds=10)
    clock.now = 8
    cache.set("k", 2, ttl_seconds=10)
    clock.now = 15
    assert cache.get("k") == 2


def test_cache_rejects_non_positive_ttl(cache):
    with pytest.raises(ValueError):
        cache.set("k", 1, ttl_seconds=0)


def test_cache_purge_removes_only_expired(cache, clock):
    cache.set("a", 1, ttl_seconds=10)
    cache.set("b", 2, ttl_seconds=100)
    clock.now = 50
    assert cache.purge_expired() == 1
    assert len(cache) == 1
    assert cache.get("b") == 2


def test_cache_delete(cache):
    cache.set("a", 1, ttl_seconds=10)
    cache.delete("a")
    cache.delete("없는키")  # 없는 키 삭제는 오류가 아니다
    assert "a" not in cache


# --- 그래프: 의존 관계와 재귀 CTE -----------------------------------------------------------------


@pytest.fixture
def graph(conn):
    """1 ← 2 ← 3 (3 은 2 가, 2 는 1 이 끝나야 한다), 4 는 독립."""
    s = SqliteTaskStore(conn)
    s.init_schema()
    for title in ["기초", "중급", "고급", "독립"]:
        s.add(title)
    s.add_dependency(2, 1)
    s.add_dependency(3, 2)
    return s


def test_migration_003_created_task_deps(graph, conn):
    assert current_version(conn) == 3
    assert conn.execute("SELECT COUNT(*) FROM task_deps").fetchone() == (2,)


def test_blockers_are_transitive(graph):
    assert graph.blockers(3) == [1, 2]  # 직접(2) + 건너서(1)
    assert graph.blockers(2) == [1]
    assert graph.blockers(1) == []
    assert graph.blockers(4) == []


def test_dependency_on_self_is_rejected(graph):
    with pytest.raises(ValueError):
        graph.add_dependency(4, 4)


def test_dependency_on_missing_task_is_rejected(graph):
    with pytest.raises(TaskNotFoundError):
        graph.add_dependency(4, 99)


def test_cycle_is_rejected(graph):
    with pytest.raises(ValueError):
        graph.add_dependency(1, 3)  # 1 → 3 을 넣으면 1 → 3 → 2 → 1 고리
    assert graph.blockers(1) == []


def test_duplicate_dependency_is_ignored(graph, conn):
    graph.add_dependency(3, 2)
    assert conn.execute("SELECT COUNT(*) FROM task_deps").fetchone() == (2,)


def test_ready_tasks_are_open_tasks_whose_blockers_are_done(graph):
    assert [t.id for t in graph.ready_tasks()] == [1, 4]
    graph.complete(1)
    assert [t.id for t in graph.ready_tasks()] == [2, 4]
    graph.complete(2)
    assert [t.id for t in graph.ready_tasks()] == [3, 4]


def test_removing_a_task_removes_its_edges(graph, conn):
    graph.remove(2)
    assert conn.execute("SELECT COUNT(*) FROM task_deps").fetchone() == (0,)
    assert graph.blockers(3) == []


def test_diamond_dependency_lists_each_blocker_once(conn):
    """4 ← 2 ← 1, 4 ← 3 ← 1: 1 은 두 경로로 닿지만 한 번만 나와야 한다 (UNION 의 역할)."""
    s = SqliteTaskStore(conn)
    s.init_schema()
    for title in "abcd":
        s.add(title)
    s.add_dependency(2, 1)
    s.add_dependency(3, 1)
    s.add_dependency(4, 2)
    s.add_dependency(4, 3)
    assert s.blockers(4) == [1, 2, 3]
