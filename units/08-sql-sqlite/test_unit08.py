"""08단원 테스트. 실행: pytest units/08-sql-sqlite

대부분의 테스트는 `sqlite3.connect(":memory:")` 로 만든 빈 DB 를 쓴다. 메모리 DB 는
연결을 닫으면 사라지므로 테스트끼리 서로 영향을 주지 않는다.
"""

import sqlite3

import pytest

from injection_demo import find_by_title_safe, find_by_title_unsafe, make_demo_db
from todo import Task, TaskNotFoundError
from todo.storage_sqlite import SqliteTaskStore


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


# --- 스키마 ---------------------------------------------------------------


def test_init_schema_creates_tasks_table(conn):
    SqliteTaskStore(conn).init_schema()
    names = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    assert "tasks" in names


def test_init_schema_can_run_twice(store):
    store.init_schema()  # 두 번째 호출이 예외를 던지면 안 된다 (IF NOT EXISTS)


def test_schema_rejects_blank_title_even_without_python(conn):
    """제약은 파이썬 코드를 거치지 않고 직접 INSERT 해도 작동해야 한다."""
    SqliteTaskStore(conn).init_schema()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO tasks (title) VALUES ('   ')")


def test_schema_rejects_done_other_than_0_or_1(conn):
    SqliteTaskStore(conn).init_schema()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO tasks (title, done) VALUES ('x', 2)")


# --- add / get ------------------------------------------------------------


def test_add_first_task_gets_id_1(store):
    task = store.add("SQL 공부")
    assert task == Task(id=1, title="SQL 공부", done=False)


def test_add_strips_whitespace(store):
    assert store.add("  산책  ").title == "산책"
    assert store.get(1).title == "산책"  # DB 에도 공백 없이 저장되어야 한다


@pytest.mark.parametrize("title", ["", "   "])
def test_add_rejects_empty_title_and_inserts_nothing(store, title):
    with pytest.raises(ValueError):
        store.add(title)
    assert len(store) == 0


def test_get_missing_raises_task_not_found(store):
    with pytest.raises(TaskNotFoundError):
        store.get(99)


def test_task_not_found_is_a_value_error(store):
    """CLI 는 `except ValueError` 하나로 두 오류를 다 잡는다. 그 관계가 유지되어야 한다."""
    with pytest.raises(ValueError):
        store.get(99)


def test_id_is_not_reused_after_removing_middle(store):
    store.add("a")
    store.add("b")
    store.remove(1)
    assert store.add("c").id == 3


# --- complete / remove ----------------------------------------------------


def test_complete_sets_done(store):
    store.add("a")
    assert store.complete(1).done is True
    assert store.get(1).done is True


def test_complete_twice_raises(store):
    store.add("a")
    store.complete(1)
    with pytest.raises(ValueError):
        store.complete(1)


def test_complete_missing_raises(store):
    with pytest.raises(TaskNotFoundError):
        store.complete(7)


def test_remove_returns_removed_task(store):
    store.add("a")
    store.add("b")
    removed = store.remove(1)
    assert removed.title == "a"
    assert [t.id for t in store.all()] == [2]


def test_remove_missing_raises(store):
    with pytest.raises(TaskNotFoundError):
        store.remove(1)


# --- all / open_tasks / len -----------------------------------------------


def test_all_is_ordered_by_id(store):
    for title in ["c", "a", "b"]:
        store.add(title)
    assert [t.id for t in store.all()] == [1, 2, 3]


def test_open_tasks_filters_done(store):
    store.add("a")
    store.add("b")
    store.complete(1)
    assert [t.id for t in store.open_tasks()] == [2]


def test_len_counts_rows(store):
    assert len(store) == 0
    store.add("a")
    store.add("b")
    assert len(store) == 2


# --- 영속성: 파일 DB 는 연결을 닫았다 열어도 남아 있어야 한다 -------------------


def test_data_survives_reconnect(tmp_path):
    path = tmp_path / "todo.db"
    first = sqlite3.connect(path)
    store = SqliteTaskStore(first)
    store.init_schema()
    store.add("기억해")
    store.complete(1)
    first.close()  # commit 하지 않은 변경은 여기서 사라진다

    second = sqlite3.connect(path)
    reopened = SqliteTaskStore(second)
    assert reopened.all() == [Task(id=1, title="기억해", done=True)]
    second.close()


# --- SQL 인젝션 ----------------------------------------------------------


def test_title_that_looks_like_sql_is_stored_as_plain_text(store):
    """`?` 를 썼다면 따옴표나 세미콜론이 들어간 제목도 그냥 글자일 뿐이다."""
    evil = "x'); DELETE FROM tasks; --"
    store.add("멀쩡한 할 일")
    task = store.add(evil)
    assert task.title == evil
    assert store.get(task.id).title == evil
    assert len(store) == 2


def test_demo_unsafe_query_leaks_every_row():
    """f-string 으로 조립한 SQL 은 입력이 문법이 되어 조건이 항상 참이 된다. (시연 — 이렇게 짜지 말 것)"""
    conn = make_demo_db()
    assert len(find_by_title_unsafe(conn, "' OR '1'='1")) == 3


def test_demo_safe_query_treats_input_as_value():
    conn = make_demo_db()
    assert find_by_title_safe(conn, "' OR '1'='1") == []
    assert find_by_title_safe(conn, "치과 예약") == [(3, "치과 예약")]
