"""09단원 테스트. 실행: pytest units/09-data-modeling"""

import json
import sqlite3

import pytest

from todo import JsonTaskStore, Task, TaskNotFoundError, normalize_tags
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


# --- 모델: 태그 표준화 (이미 구현되어 있음 — 규칙을 읽어 두세요) ---------------------


def test_normalize_tags_strips_dedupes_and_sorts():
    assert normalize_tags([" 공부 ", "운동", "공부", "", "  "]) == ["공부", "운동"]


def test_task_normalizes_tags_on_creation():
    assert Task(id=1, title="a", tags=["b", "a", "b"]).tags == ["a", "b"]


def test_json_store_round_trips_tags(tmp_path):
    store = JsonTaskStore(tmp_path / "t.json")
    store.save([Task(id=1, title="a", tags=["x", "y"])])
    assert store.load()[0].tags == ["x", "y"]


def test_json_store_reads_files_saved_before_tags_existed(tmp_path):
    """08단원까지 저장한 파일에는 tags 키가 없다. 그래도 읽혀야 한다 (하위 호환)."""
    path = tmp_path / "old.json"
    path.write_text(json.dumps([{"id": 1, "title": "옛날 할 일", "done": False}]), encoding="utf-8")
    assert JsonTaskStore(path).load() == [Task(id=1, title="옛날 할 일")]


# --- 스키마 -----------------------------------------------------------------


def test_schema_has_three_tables(store, conn):
    names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"tasks", "tags", "task_tags"} <= names


def test_tag_names_are_unique(store, conn):
    conn.execute("INSERT INTO tags (name) VALUES ('x')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO tags (name) VALUES ('x')")


def test_link_to_missing_task_is_rejected(store, conn):
    """외래 키(FK) 가 켜져 있으면 존재하지 않는 할 일에 태그를 연결할 수 없다."""
    conn.execute("INSERT INTO tags (name) VALUES ('x')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (999, 1)")


def test_same_tag_cannot_be_linked_twice(store, conn):
    store.add("a", tags=["x"])
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (1, 1)")


# --- add / get -----------------------------------------------------------------


def test_add_without_tags_still_works(store):
    assert store.add("a") == Task(id=1, title="a")


def test_add_with_tags_returns_normalized_tags(store):
    task = store.add("a", tags=[" 운동 ", "공부", "운동"])
    assert task.tags == ["공부", "운동"]
    assert store.get(1).tags == ["공부", "운동"]


def test_add_rejects_empty_title_and_stores_no_tag_links(store, conn):
    with pytest.raises(ValueError):
        store.add("  ", tags=["x"])
    assert conn.execute("SELECT COUNT(*) FROM task_tags").fetchone() == (0,)


def test_same_tag_name_is_stored_once(store, conn):
    store.add("a", tags=["공부"])
    store.add("b", tags=["공부", "운동"])
    assert conn.execute("SELECT COUNT(*) FROM tags").fetchone() == (2,)


def test_all_and_open_tasks_include_tags(store):
    store.add("a", tags=["x"])
    store.add("b")
    store.complete(2)
    assert [t.tags for t in store.all()] == [["x"], []]
    assert store.open_tasks() == [Task(id=1, title="a", tags=["x"])]


def test_complete_keeps_tags(store):
    store.add("a", tags=["x"])
    assert store.complete(1).tags == ["x"]


# --- by_tag ----------------------------------------------------------------------


def test_by_tag_returns_tasks_in_id_order(store):
    store.add("c", tags=["공부"])
    store.add("b", tags=["운동"])
    store.add("a", tags=["공부", "운동"])
    assert [t.id for t in store.by_tag("공부")] == [1, 3]
    assert [t.id for t in store.by_tag("운동")] == [2, 3]


def test_by_tag_unknown_tag_returns_empty_list(store):
    store.add("a", tags=["x"])
    assert store.by_tag("없는태그") == []


def test_by_tag_strips_whitespace(store):
    store.add("a", tags=["x"])
    assert [t.id for t in store.by_tag("  x ")] == [1]


# --- remove 와 CASCADE -------------------------------------------------------------


def test_remove_deletes_links_but_keeps_tag_row(store, conn):
    store.add("a", tags=["x"])
    store.remove(1)
    assert conn.execute("SELECT COUNT(*) FROM task_tags").fetchone() == (0,)
    assert conn.execute("SELECT COUNT(*) FROM tags").fetchone() == (1,)  # 태그 자체는 남는다
    assert store.by_tag("x") == []


def test_remove_missing_raises(store):
    with pytest.raises(TaskNotFoundError):
        store.remove(1)


# --- tag_counts (GROUP BY) -----------------------------------------------------------


def test_tag_counts_groups_by_tag(store):
    store.add("a", tags=["공부"])
    store.add("b", tags=["공부", "운동"])
    store.add("c", tags=["운동"])
    store.add("d")
    assert store.tag_counts() == {"공부": 2, "운동": 2}


def test_tag_counts_drops_tags_no_longer_used(store):
    store.add("a", tags=["x"])
    store.remove(1)
    assert store.tag_counts() == {}


def test_tag_counts_empty_db(store):
    assert store.tag_counts() == {}
