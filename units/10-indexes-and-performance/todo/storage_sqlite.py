"""10단원: SQLite 저장소에 인덱스를 더한다.

09단원까지의 코드는 완성되어 있다. 이번 단원의 TODO 는 SCHEMA 의 인덱스 한 줄뿐이다 —
대신 `scripts/bench.py` 로 **그 한 줄이 무엇을 바꾸는지 측정**하는 것이 과제의 중심이다.
"""

from __future__ import annotations

import sqlite3
from typing import Iterable

from .models import Task, TaskNotFoundError, normalize_tags

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id    INTEGER PRIMARY KEY,
    title TEXT    NOT NULL CHECK (length(trim(title)) > 0),
    done  INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
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

-- TODO: 접근 패턴 B(태그로 거르기)를 위한 인덱스를 만든다. 이름은 반드시 idx_task_tags_tag.
--   복합 PK (task_id, tag_id) 는 "task_id 먼저" 정렬이라 tag_id 만으로 찾을 때 쓸 수 없다.
--   힌트: CREATE INDEX IF NOT EXISTS 이름 ON 테이블 (열);
"""

SELECT_COLUMNS = "id, title, done"


class SqliteTaskStore:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.conn.execute("PRAGMA foreign_keys = ON")

    def init_schema(self) -> None:
        self.conn.executescript(SCHEMA)

    # --- 내부 도우미 ---

    def _row_to_task(self, row: tuple) -> Task:
        task_id, title, done = row
        return Task(id=task_id, title=title, done=bool(done), tags=self._tags_of(task_id))

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

    def _attach_tag(self, task_id: int, tag: str) -> None:
        self.conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        (tag_id,) = self.conn.execute("SELECT id FROM tags WHERE name = ?", (tag,)).fetchone()
        self.conn.execute(
            "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)", (task_id, tag_id)
        )

    # --- 공개 메서드 ---

    def add(self, title: str, tags: Iterable[str] = ()) -> Task:
        title = title.strip()
        tags = normalize_tags(tags)
        try:
            cursor = self.conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        except sqlite3.IntegrityError as error:
            raise ValueError("제목은 비어 있을 수 없습니다") from error
        task_id = cursor.lastrowid
        for tag in tags:
            self._attach_tag(task_id, tag)
        self.conn.commit()
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
        self.conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        self.conn.commit()
        return self.get(task_id)

    def remove(self, task_id: int) -> Task:
        task = self.get(task_id)
        self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
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
            """
            SELECT tasks.id, tasks.title, tasks.done
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
