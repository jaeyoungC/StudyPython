"""11단원: 트랜잭션과 낙관적 잠금.

10단원까지의 코드는 완성되어 있고, 쓰기 메서드는 `self.conn.commit()` 대신 `with self.conn:` 을 쓰도록
이미 바꿔 두었다 (블록이 정상 종료하면 commit, 예외가 나가면 rollback). `tasks.version` 열과
`Task.version` 필드도 들어 있다. `complete()` 가 version 을 올리는 방식을 참고하라.

이번 단원의 TODO 는 두 메서드:
  - rename(task_id, new_title, expected_version=None)  : 낙관적 잠금(optimistic locking)
  - move_tag(task_id, from_tag, to_tag)                 : 두 문장을 한 트랜잭션으로
"""

from __future__ import annotations

import sqlite3
from typing import Iterable

from .models import Task, TaskNotFoundError, normalize_tags

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id      INTEGER PRIMARY KEY,
    title   TEXT    NOT NULL CHECK (length(trim(title)) > 0),
    done    INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1)),
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS tags (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0)
);

CREATE TABLE IF NOT EXISTS task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id  INTEGER NOT NULL REFERENCES tags(id)  ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_task_tags_tag ON task_tags (tag_id);
"""

SELECT_COLUMNS = "id, title, done, version"


class ConflictError(Exception):
    """내가 읽은 뒤 다른 누군가가 먼저 바꿨다 (version 이 달라짐). 다시 읽고 다시 시도해야 한다."""


class SqliteTaskStore:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.conn.execute("PRAGMA foreign_keys = ON")

    def init_schema(self) -> None:
        self.conn.executescript(SCHEMA)

    # --- 내부 도우미 ---

    def _row_to_task(self, row: tuple) -> Task:
        task_id, title, done, version = row
        return Task(id=task_id, title=title, done=bool(done), tags=self._tags_of(task_id), version=version)

    def _tags_of(self, task_id: int) -> list[str]:
        rows = self.conn.execute(
            """
            SELECT tags.name
            FROM task_tags
            JOIN tags ON tags.id = task_tags.tag_id
            WHERE task_tags.task_id = ?
            ORDER BY tags.name
            """,
            (task_id,),
        ).fetchall()
        return [name for (name,) in rows]

    def _tag_id(self, tag: str) -> int:
        self.conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        (tag_id,) = self.conn.execute("SELECT id FROM tags WHERE name = ?", (tag,)).fetchone()
        return tag_id

    def _attach_tag(self, task_id: int, tag: str) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)", (task_id, self._tag_id(tag))
        )

    # --- 공개 메서드 ---

    def add(self, title: str, tags: Iterable[str] = ()) -> Task:
        title = title.strip()
        tags = normalize_tags(tags)
        with self.conn:
            try:
                cursor = self.conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
            except sqlite3.IntegrityError as error:
                raise ValueError("제목은 비어 있을 수 없습니다") from error
            task_id = cursor.lastrowid
            for tag in tags:
                self._attach_tag(task_id, tag)
        return Task(id=task_id, title=title, tags=tags)

    def get(self, task_id: int) -> Task:
        row = self.conn.execute(
            f"SELECT {SELECT_COLUMNS} FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            raise TaskNotFoundError(task_id)
        return self._row_to_task(row)

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        if task.done:
            raise ValueError(f"할 일 #{task_id} 은(는) 이미 완료되었습니다")
        with self.conn:
            self.conn.execute(
                "UPDATE tasks SET done = 1, version = version + 1 WHERE id = ?", (task_id,)
            )
        return self.get(task_id)

    def rename(self, task_id: int, new_title: str, expected_version: int | None = None) -> Task:
        """제목을 바꾸고 version 을 1 올린다.

        - 앞뒤 공백 제거, 빈 제목은 ValueError (DB 에 가기 전에 검사).
        - expected_version 이 None 이면 그냥 UPDATE 한다 (마지막 쓰기가 이긴다 — lost update 가 가능하다).
        - expected_version 이 주어지면 `WHERE id = ? AND version = ?` 로 UPDATE 한다.
          바뀐 행이 0 개(cursor.rowcount == 0)이면:
            * 할 일이 아예 없으면 TaskNotFoundError (get() 을 부르면 알아서 던진다)
            * 있는데 version 이 다르면 ConflictError
        - 돌려주는 값은 바뀐 뒤의 Task.
        힌트: UPDATE 가 돌려준 커서의 `rowcount` 가 "실제로 바뀐 행 수"다.
        """
        # TODO
        raise NotImplementedError

    def move_tag(self, task_id: int, from_tag: str, to_tag: str) -> Task:
        """할 일에서 from_tag 를 떼고 to_tag 를 붙인다. 둘은 **같이 성공하거나 같이 실패**해야 한다.

        - from_tag 가 붙어 있지 않으면 ValueError. to_tag 가 비어 있으면 ValueError.
        - to_tag 가 이미 붙어 있으면 INSERT 가 IntegrityError 를 내는데(복합 PK), 이때 앞서 한 DELETE 도
          없던 일이 되어야 한다 → DELETE 와 INSERT 를 같은 `with self.conn:` 블록 안에서 실행하고,
          IntegrityError 는 ValueError 로 바꿔 다시 던진다 (`raise ... from`). 블록을 예외가 빠져나가면 롤백된다.
          주의: `_attach_tag` 는 INSERT OR IGNORE 라서 실패하지 않는다. 여기서는 그냥 INSERT 를 쓰자 (`_tag_id` 는 재사용 가능).
        - 성공하면 version 을 1 올리고 바뀐 Task 를 돌려준다.
        """
        # TODO
        raise NotImplementedError

    def remove(self, task_id: int) -> Task:
        task = self.get(task_id)
        with self.conn:
            self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return task

    def all(self) -> list[Task]:
        rows = self.conn.execute(f"SELECT {SELECT_COLUMNS} FROM tasks ORDER BY id").fetchall()
        return [self._row_to_task(row) for row in rows]

    def open_tasks(self) -> list[Task]:
        rows = self.conn.execute(
            f"SELECT {SELECT_COLUMNS} FROM tasks WHERE done = 0 ORDER BY id"
        ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def by_tag(self, tag: str) -> list[Task]:
        rows = self.conn.execute(
            f"""
            SELECT {", ".join("tasks." + c for c in SELECT_COLUMNS.split(", "))}
            FROM tasks
            JOIN task_tags ON task_tags.task_id = tasks.id
            JOIN tags      ON tags.id = task_tags.tag_id
            WHERE tags.name = ?
            ORDER BY tasks.id
            """,
            (tag.strip(),),
        ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def tag_counts(self) -> dict[str, int]:
        rows = self.conn.execute(
            """
            SELECT tags.name, COUNT(task_tags.task_id)
            FROM tags
            JOIN task_tags ON task_tags.tag_id = tags.id
            GROUP BY tags.id
            ORDER BY tags.name
            """
        ).fetchall()
        return {name: count for name, count in rows}

    def __len__(self) -> int:
        (count,) = self.conn.execute("SELECT COUNT(*) FROM tasks").fetchone()
        return count
