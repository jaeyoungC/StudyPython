"""11단원 테스트. 실행: pytest units/11-transactions-and-concurrency

스레드 테스트는 파일 DB(tmp_path) 를 쓴다. `:memory:` DB 는 연결마다 따로 만들어져서
두 스레드가 같은 데이터를 볼 수 없기 때문이다. 스레드마다 연결을 하나씩 연다.
"""

import sqlite3
import threading

import pytest

from todo import Task, TaskNotFoundError
from todo.storage_sqlite import ConflictError, SqliteTaskStore


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


# --- `with conn:` 의 동작 (sqlite3 자체를 확인하는 학습용 테스트) -------------------------


def test_with_conn_commits_when_block_succeeds(tmp_path):
    path = tmp_path / "t.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE n (v INTEGER)")
    with conn:
        conn.execute("INSERT INTO n VALUES (1)")
    conn.close()
    assert sqlite3.connect(path).execute("SELECT COUNT(*) FROM n").fetchone() == (1,)


def test_with_conn_rolls_back_when_block_raises(conn):
    conn.execute("CREATE TABLE n (v INTEGER)")
    conn.commit()
    with pytest.raises(RuntimeError):
        with conn:
            conn.execute("INSERT INTO n VALUES (1)")
            conn.execute("INSERT INTO n VALUES (2)")
            raise RuntimeError("중간에 실패")
    assert conn.execute("SELECT COUNT(*) FROM n").fetchone() == (0,)  # 둘 다 없던 일이 된다


# --- version 열 ------------------------------------------------------------------------


def test_new_task_has_version_1(store):
    assert store.add("a").version == 1
    assert store.get(1).version == 1


def test_complete_bumps_version(store):
    store.add("a")
    assert store.complete(1).version == 2


def test_rename_changes_title_and_bumps_version(store):
    store.add("a")
    task = store.rename(1, "  b  ")
    assert task.title == "b"
    assert task.version == 2
    assert store.get(1) == Task(id=1, title="b", version=2)


def test_rename_rejects_empty_title(store):
    store.add("a")
    with pytest.raises(ValueError):
        store.rename(1, "   ")
    assert store.get(1).title == "a"


def test_rename_missing_task_raises(store):
    with pytest.raises(TaskNotFoundError):
        store.rename(99, "b")


def test_rename_with_matching_version_succeeds(store):
    task = store.add("a")
    assert store.rename(1, "b", expected_version=task.version).version == 2


def test_rename_with_stale_version_raises_conflict_and_changes_nothing(store):
    task = store.add("a")  # version 1
    store.complete(1)  # 누군가 먼저 바꿔서 version 2
    with pytest.raises(ConflictError):
        store.rename(1, "b", expected_version=task.version)
    assert store.get(1).title == "a"
    assert store.get(1).version == 2


def test_rename_missing_task_with_version_raises_not_found(store):
    with pytest.raises(TaskNotFoundError):
        store.rename(99, "b", expected_version=1)


# --- move_tag 트랜잭션 -------------------------------------------------------------------


def test_move_tag_replaces_one_tag_with_another(store):
    store.add("a", tags=["급함", "집"])
    task = store.move_tag(1, "급함", "나중에")
    assert task.tags == ["나중에", "집"]
    assert task.version == 2


def test_move_tag_unknown_from_tag_raises(store):
    store.add("a", tags=["집"])
    with pytest.raises(ValueError):
        store.move_tag(1, "급함", "나중에")
    assert store.get(1).tags == ["집"]


def test_move_tag_missing_task_raises(store):
    with pytest.raises(TaskNotFoundError):
        store.move_tag(42, "a", "b")


def test_move_tag_rolls_back_when_target_already_attached(store):
    """삭제는 성공했는데 추가가 실패하면? 트랜잭션이 아니면 태그 하나가 그냥 사라진다."""
    store.add("a", tags=["급함", "집"])
    with pytest.raises(ValueError):
        store.move_tag(1, "급함", "집")  # '집' 은 이미 붙어 있어 INSERT 가 실패한다
    assert store.get(1).tags == ["급함", "집"]  # '급함' 삭제도 없던 일이 되어야 한다
    assert store.get(1).version == 1


# --- 두 스레드: lost update 재현과 낙관적 잠금 ------------------------------------------------


def run_two_writers(path, make_new_title, use_version):
    """스레드 두 개가 같은 할 일을 '읽고 → (둘 다 읽을 때까지 기다리고) → 고쳐 쓴다'.

    Barrier 가 두 스레드의 읽기를 쓰기보다 먼저 끝내도록 강제하므로 결과가 실행마다 같다.
    돌려주는 값: 각 스레드가 받은 예외 목록 (성공하면 None).
    """
    barrier = threading.Barrier(2)
    outcomes: list[BaseException | None] = [None, None]

    def worker(index: int, suffix: str) -> None:
        conn = sqlite3.connect(path, timeout=5)  # 스레드마다 자기 연결
        try:
            store = SqliteTaskStore(conn)
            task = store.get(1)  # 1. 읽기
            barrier.wait(timeout=5)  # 2. 상대도 읽을 때까지 대기
            kwargs = {"expected_version": task.version} if use_version else {}
            store.rename(1, make_new_title(task.title, suffix), **kwargs)  # 3. 쓰기
        except BaseException as error:  # noqa: BLE001 — 테스트에서 결과를 모으기 위해
            outcomes[index] = error
        finally:
            conn.close()

    threads = [threading.Thread(target=worker, args=(0, "A")), threading.Thread(target=worker, args=(1, "B"))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
    return outcomes


@pytest.fixture
def shared_db(tmp_path):
    path = tmp_path / "shared.db"
    conn = sqlite3.connect(path)
    store = SqliteTaskStore(conn)
    store.init_schema()
    store.add("제목")
    conn.close()
    return path


def test_two_writers_without_version_check_lose_one_update(shared_db):
    """lost update 재현: 둘 다 성공했다고 믿지만 한쪽의 변경은 사라진다."""
    outcomes = run_two_writers(shared_db, lambda title, suffix: title + suffix, use_version=False)
    assert outcomes == [None, None]  # 둘 다 예외 없이 끝났는데
    (title,) = sqlite3.connect(shared_db).execute("SELECT title FROM tasks WHERE id = 1").fetchone()
    assert title in ("제목A", "제목B")  # 결과에는 한 쪽만 남는다 ("제목AB" 가 아니다)


def test_two_writers_with_version_check_detect_the_conflict(shared_db):
    """낙관적 잠금: 늦게 쓴 쪽은 ConflictError 를 받는다. 변경이 조용히 사라지지 않는다."""
    outcomes = run_two_writers(shared_db, lambda title, suffix: title + suffix, use_version=True)
    successes = [o for o in outcomes if o is None]
    conflicts = [o for o in outcomes if isinstance(o, ConflictError)]
    assert len(successes) == 1 and len(conflicts) == 1, outcomes
    conn = sqlite3.connect(shared_db)
    title, version = conn.execute("SELECT title, version FROM tasks WHERE id = 1").fetchone()
    assert title in ("제목A", "제목B")
    assert version == 2  # 정확히 한 번만 바뀌었다
