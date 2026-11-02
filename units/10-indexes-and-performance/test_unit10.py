"""10단원 테스트. 실행: pytest units/10-indexes-and-performance

성능 자체는 테스트하지 않는다 (컴퓨터마다 다르고, 느린 CI 에서 깨진다). 테스트는
"인덱스가 존재하고, 쿼리 플랜이 그 인덱스를 쓴다"는 **구조적 사실**만 확인한다.
숫자는 scripts/bench.py 로 직접 재서 NOTES.md 에 적는다.
"""

import importlib.util
import random
import sqlite3
from pathlib import Path

import pytest

from todo.storage_sqlite import SqliteTaskStore

BENCH_PATH = Path(__file__).parent / "scripts" / "bench.py"
BY_TAG_SQL = """
SELECT tasks.id, tasks.title, tasks.done
FROM tasks
JOIN task_tags ON task_tags.task_id = tasks.id
JOIN tags      ON tags.id = task_tags.tag_id
WHERE tags.name = ?
ORDER BY tasks.id
"""


def load_bench():
    """scripts/ 는 패키지가 아니므로 파일 경로로 모듈을 불러온다."""
    spec = importlib.util.spec_from_file_location("bench_unit10", BENCH_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def store(conn):
    s = SqliteTaskStore(conn)
    s.init_schema()
    return s


def explain(conn, sql, params=()):
    return " | ".join(row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + sql, params))


# --- 인덱스 존재 ----------------------------------------------------------------


def test_tag_index_exists(store, conn):
    names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'")}
    assert "idx_task_tags_tag" in names


def test_tag_index_is_on_task_tags_tag_id(store, conn):
    (table,) = conn.execute(
        "SELECT tbl_name FROM sqlite_master WHERE type = 'index' AND name = 'idx_task_tags_tag'"
    ).fetchone()
    assert table == "task_tags"
    columns = [row[2] for row in conn.execute("PRAGMA index_info('idx_task_tags_tag')")]
    assert columns == ["tag_id"]


def test_init_schema_twice_does_not_duplicate_index(store, conn):
    store.init_schema()
    (count,) = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type = 'index' AND name = 'idx_task_tags_tag'"
    ).fetchone()
    assert count == 1


# --- 쿼리 플랜 --------------------------------------------------------------------


def test_by_tag_plan_uses_the_index(store, conn):
    store.add("a", tags=["x"])
    text = explain(conn, BY_TAG_SQL, ("x",))
    assert "idx_task_tags_tag" in text


def test_by_tag_plan_scans_without_the_index(store, conn):
    """대조군: 인덱스를 지우면 플랜에 SCAN(전체 훑기)이 나타난다. 인덱스가 하는 일을 눈으로 보는 테스트."""
    conn.execute("DROP INDEX idx_task_tags_tag")
    text = explain(conn, BY_TAG_SQL, ("x",))
    assert "idx_task_tags_tag" not in text
    assert "SCAN" in text


def test_primary_key_lookup_needs_no_extra_index(store, conn):
    """INTEGER PRIMARY KEY 는 그 자체가 인덱스다. get(id) 에 별도 인덱스는 필요 없다."""
    text = explain(conn, "SELECT id, title, done FROM tasks WHERE id = ?", (1,))
    assert "SEARCH" in text and "PRIMARY KEY" in text


def test_unique_constraint_created_an_automatic_index(store, conn):
    """UNIQUE 제약은 SQLite 가 자동으로 인덱스를 만든다. tags.name 검색이 빠른 이유."""
    text = explain(conn, "SELECT id FROM tags WHERE name = ?", ("x",))
    assert "sqlite_autoindex_tags_1" in text


# --- 저장소 동작은 그대로여야 한다 -----------------------------------------------------


def test_store_behaviour_unchanged(store):
    store.add("a", tags=["x", "y"])
    store.add("b", tags=["y"])
    assert [t.id for t in store.by_tag("y")] == [1, 2]
    assert store.tag_counts() == {"x": 1, "y": 2}


# --- bench.py ---------------------------------------------------------------------


def test_generate_inserts_requested_rows(store, conn):
    bench = load_bench()
    bench.generate(conn, n_tasks=200, n_tags=5, rng=random.Random(1))
    assert len(store) == 200
    assert conn.execute("SELECT COUNT(*) FROM tags").fetchone() == (5,)
    (links,) = conn.execute("SELECT COUNT(*) FROM task_tags").fetchone()
    assert 200 <= links <= 600  # 할 일마다 1~3개


def test_generate_is_reproducible_with_same_seed():
    bench = load_bench()
    results = []
    for _ in range(2):
        conn = sqlite3.connect(":memory:")
        SqliteTaskStore(conn).init_schema()
        bench.generate(conn, n_tasks=50, n_tags=4, rng=random.Random(7))
        results.append(conn.execute("SELECT * FROM task_tags ORDER BY 1, 2").fetchall())
        conn.close()
    assert results[0] == results[1]


def test_measure_runs_fn_repeat_times_and_returns_milliseconds():
    bench = load_bench()
    calls = []
    elapsed = bench.measure(lambda: calls.append(1), repeat=3)
    assert len(calls) == 3
    assert isinstance(elapsed, float) and elapsed >= 0


def test_plan_helper_returns_plan_text(store, conn):
    bench = load_bench()
    text = bench.plan(conn, BY_TAG_SQL, ("x",))
    assert "idx_task_tags_tag" in text


def test_bench_insert_adds_rows(store, conn):
    bench = load_bench()
    elapsed = bench.bench_insert(conn, 10, random.Random(3))
    assert elapsed >= 0
    assert len(store) == 10
