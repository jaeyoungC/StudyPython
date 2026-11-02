"""12단원 테스트. 실행: pytest units/12-migrations-and-backup"""

import sqlite3
from datetime import date
from pathlib import Path

import pytest

from todo import JsonTaskStore, Task
from todo.backup import backup_to, restore_from
from todo.migrate import MIGRATIONS_DIR, MigrationError, current_version, load_migrations, migrate, pending
from todo.storage_sqlite import SqliteTaskStore


class NotYetImplemented:
    """픽스처 안에서 아직 구현되지 않은 메서드를 만났을 때 돌려주는 대역.

    픽스처에서 예외가 나면 pytest 는 ERROR 로 표시한다. 대신 이 객체를 돌려주고, 테스트가 처음 쓰는 순간
    분명한 메시지로 FAILED 가 되게 한다.
    """

    def __init__(self, what: str) -> None:
        self.what = what

    def _fail(self, *args, **kwargs):
        pytest.fail(f"{self.what} 을(를) 아직 구현하지 않음")

    __getattr__ = __len__ = __iter__ = __call__ = _fail

# 11단원 시절 init_schema() 가 만들던 스키마 (마이그레이션 도입 전, user_version = 0 인 DB 를 흉내 낸다)
LEGACY_SCHEMA = """
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY, title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1)), version INTEGER NOT NULL DEFAULT 1);
CREATE TABLE tags (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE, PRIMARY KEY (task_id, tag_id));
CREATE INDEX idx_task_tags_tag ON task_tags (tag_id);
"""


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def store(conn):
    s = SqliteTaskStore(conn)
    try:
        s.init_schema()  # 안에서 migrate() 를 부른다
    except NotImplementedError:
        return NotYetImplemented("migrate()")
    return s


def columns(conn, table):
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


# --- 마이그레이션 파일 읽기 ----------------------------------------------------------


def test_repo_has_two_migrations_in_order():
    numbers = [number for number, _ in load_migrations(MIGRATIONS_DIR)]
    assert numbers == [1, 2]


def test_load_migrations_sorts_by_number_and_ignores_other_files(tmp_path):
    for name in ["010_later.sql", "002_second.sql", "001_first.sql", "README.md", "003_draft.sql.bak"]:
        (tmp_path / name).write_text("SELECT 1;")
    assert [n for n, _ in load_migrations(tmp_path)] == [1, 2, 10]
    assert [p.name for _, p in load_migrations(tmp_path)] == ["001_first.sql", "002_second.sql", "010_later.sql"]


def test_duplicate_number_is_an_error(tmp_path):
    (tmp_path / "001_a.sql").write_text("SELECT 1;")
    (tmp_path / "001_b.sql").write_text("SELECT 1;")
    with pytest.raises(MigrationError):
        load_migrations(tmp_path)


# --- 적용 -------------------------------------------------------------------------------


def test_fresh_db_starts_at_version_0(conn):
    assert current_version(conn) == 0


def test_migrate_applies_all_and_sets_user_version(conn):
    assert migrate(conn) == [1, 2]
    assert current_version(conn) == 2
    assert "due" in columns(conn, "tasks")


def test_migrate_is_idempotent(conn):
    migrate(conn)
    assert migrate(conn) == []
    assert pending(conn) == []
    assert current_version(conn) == 2


def test_migrate_to_target_applies_only_up_to_that_number(conn):
    assert migrate(conn, target=1) == [1]
    assert current_version(conn) == 1
    assert "due" not in columns(conn, "tasks")
    assert [n for n, _ in pending(conn)] == [2]


def test_migrating_a_db_with_data_keeps_the_data(conn):
    """실전과 같은 상황: 1번까지 적용된 DB 에 데이터가 있고, 2번을 적용한다."""
    migrate(conn, target=1)
    conn.execute("INSERT INTO tasks (title) VALUES ('옛날 할 일')")
    conn.commit()
    assert migrate(conn) == [2]
    assert conn.execute("SELECT title, due FROM tasks").fetchall() == [("옛날 할 일", None)]


def test_legacy_db_without_user_version_can_be_migrated(conn):
    """마이그레이션 도입 전(11단원)에 만든 DB: 테이블은 있는데 user_version 은 0. 001 이 IF NOT EXISTS 라서 그대로 적용된다."""
    conn.executescript(LEGACY_SCHEMA)
    conn.execute("INSERT INTO tasks (title) VALUES ('11단원 데이터')")
    conn.commit()
    migrate(conn)
    assert current_version(conn) == 2
    assert conn.execute("SELECT title, due FROM tasks").fetchall() == [("11단원 데이터", None)]


def test_failed_migration_rolls_back_and_keeps_version(tmp_path, conn):
    (tmp_path / "001_ok.sql").write_text("CREATE TABLE a (x INTEGER);")
    (tmp_path / "002_bad.sql").write_text("CREATE TABLE b (x INTEGER);\nINSERT INTO no_such_table VALUES (1);")
    with pytest.raises(MigrationError):
        migrate(conn, directory=tmp_path)
    assert current_version(conn) == 1  # 002 는 없던 일
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "a" in tables and "b" not in tables  # 002 의 첫 문장도 되돌아갔다


def test_init_schema_uses_migrations(store, conn):
    assert current_version(conn) == 2
    store.init_schema()  # 두 번째 호출도 안전


# --- due 열 -----------------------------------------------------------------------------


def test_add_with_due_round_trips_a_date(store):
    task = store.add("세금 신고", due=date(2026, 5, 31))
    assert task.due == date(2026, 5, 31)
    assert store.get(1).due == date(2026, 5, 31)
    assert store.all()[0].due == date(2026, 5, 31)


def test_add_without_due_is_none(store):
    assert store.add("a").due is None
    assert store.get(1).due is None


def test_json_store_round_trips_due(tmp_path):
    json_store = JsonTaskStore(tmp_path / "t.json")
    json_store.save([Task(id=1, title="a", due=date(2026, 1, 2)), Task(id=2, title="b")])
    loaded = json_store.load()
    assert loaded[0].due == date(2026, 1, 2)
    assert loaded[1].due is None


# --- 백업과 복구 ---------------------------------------------------------------------------


def test_backup_creates_a_valid_sqlite_file(store, tmp_path):
    store.add("a", tags=["x"])
    path = backup_to(store.conn, tmp_path / "backups" / "todo.bak")
    assert path.exists()
    copy = sqlite3.connect(path)
    assert copy.execute("PRAGMA integrity_check").fetchone() == ("ok",)
    assert SqliteTaskStore(copy).all() == [Task(id=1, title="a", tags=["x"])]
    assert current_version(copy) == 2  # 스키마 버전도 함께 복사된다
    copy.close()


def test_backup_is_a_snapshot_not_a_link(store, tmp_path):
    store.add("a")
    path = backup_to(store.conn, tmp_path / "todo.bak")
    store.add("b")  # 백업 뒤의 변경은
    copy = sqlite3.connect(path)
    assert len(SqliteTaskStore(copy)) == 1  # 백업에 반영되지 않는다
    copy.close()


def test_restore_drill_brings_deleted_tasks_back(store, tmp_path):
    """복구 연습: 백업 → 실수로 전부 삭제 → 복구 → 원래대로."""
    store.add("a", tags=["x"], due=date(2026, 1, 1))
    store.add("b")
    before = store.all()
    path = backup_to(store.conn, tmp_path / "todo.bak")

    for task in store.all():
        store.remove(task.id)
    assert len(store) == 0

    restore_from(path, store.conn)
    assert store.all() == before
    assert store.by_tag("x") == [before[0]]


def test_restore_replaces_everything_in_target(store, tmp_path):
    store.add("백업에 있는 것")
    path = backup_to(store.conn, tmp_path / "todo.bak")
    store.add("백업 뒤에 추가한 것")
    restore_from(path, store.conn)
    assert [t.title for t in store.all()] == ["백업에 있는 것"]
