"""SQLite 저장소 (12단원 완성본: 스키마는 migrations/ 가 소유, due 열)."""

from __future__ import annotations

import sqlite3
from typing import Iterable

from datetime import date

from .migrate import migrate
from .models import Task, TaskNotFoundError, normalize_tags

SELECT_COLUMNS = "id, title, done, version, due"


class ConflictError(Exception):
    """내가 읽은 뒤 다른 누군가가 먼저 바꿨다 (version 이 달라짐). 다시 읽고 다시 시도해야 한다."""


class SqliteTaskStore:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.conn.execute("PRAGMA foreign_keys = ON")

    def init_schema(self) -> None:
        """스키마는 todo/migrations/*.sql 이 정의한다. 아직 적용되지 않은 번호만 순서대로 적용한다."""
        migrate(self.conn)

    # --- 내부 도우미 ---

    def _row_to_task(self, row: tuple) -> Task:
        task_id, title, done, version, due = row
        return Task(
            id=task_id,
            title=title,
            done=bool(done),
            tags=self._tags_of(task_id),
            version=version,
            due=date.fromisoformat(due) if due else None,
        )

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

    def add(self, title: str, tags: Iterable[str] = (), due: date | None = None) -> Task:
        title = title.strip()
        tags = normalize_tags(tags)
        with self.conn:
            try:
                cursor = self.conn.execute(
                    "INSERT INTO tasks (title, due) VALUES (?, ?)",
                    (title, due.isoformat() if due else None),
                )
            except sqlite3.IntegrityError as error:
                raise ValueError("제목은 비어 있을 수 없습니다") from error
            task_id = cursor.lastrowid
            for tag in tags:
                self._attach_tag(task_id, tag)
        return Task(id=task_id, title=title, tags=tags, due=due)

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
        new_title = new_title.strip()
        if not new_title:
            raise ValueError("제목은 비어 있을 수 없습니다")
        with self.conn:
            if expected_version is None:
                cursor = self.conn.execute(
                    "UPDATE tasks SET title = ?, version = version + 1 WHERE id = ?",
                    (new_title, task_id),
                )
            else:
                cursor = self.conn.execute(
                    "UPDATE tasks SET title = ?, version = version + 1 WHERE id = ? AND version = ?",
                    (new_title, task_id, expected_version),
                )
            if cursor.rowcount == 0:
                current = self.get(task_id)  # 없으면 여기서 TaskNotFoundError
                raise ConflictError(
                    f"할 일 #{task_id} 은(는) version {expected_version} 이후에 바뀌었습니다 (현재 {current.version})"
                )
        return self.get(task_id)

    def move_tag(self, task_id: int, from_tag: str, to_tag: str) -> Task:
        from_tag, to_tag = from_tag.strip(), to_tag.strip()
        if not to_tag:
            raise ValueError("옮겨 갈 태그 이름이 비어 있습니다")
        task = self.get(task_id)
        if from_tag not in task.tags:
            raise ValueError(f"할 일 #{task_id} 에는 태그 '{from_tag}' 이(가) 없습니다")
        with self.conn:
            self.conn.execute(
                "DELETE FROM task_tags WHERE task_id = ? AND tag_id = (SELECT id FROM tags WHERE name = ?)",
                (task_id, from_tag),
            )
            try:
                self.conn.execute(
                    "INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)", (task_id, self._tag_id(to_tag))
                )
            except sqlite3.IntegrityError as error:
                raise ValueError(f"할 일 #{task_id} 에는 이미 태그 '{to_tag}' 이(가) 있습니다") from error
            self.conn.execute("UPDATE tasks SET version = version + 1 WHERE id = ?", (task_id,))
        return self.get(task_id)

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
