"""문서형(document) 저장소 (13단원 완성본): 할 일 하나 = JSON 문서 하나."""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from typing import Any, Iterable

from .models import Task, TaskNotFoundError, normalize_tags

SCHEMA = """
CREATE TABLE IF NOT EXISTS task_documents (
    id   INTEGER PRIMARY KEY,
    body TEXT NOT NULL CHECK (json_valid(body))
);
"""


class DocumentTaskStore:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def init_schema(self) -> None:
        self.conn.executescript(SCHEMA)

    # --- 문서 ↔ Task ---

    @staticmethod
    def _to_document(task: Task) -> str:
        data = task.to_dict()
        del data["id"]  # id 는 열에 있으므로 문서 안에는 넣지 않는다
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def _to_task(task_id: int, body: str) -> Task:
        return Task(id=task_id, **json.loads(body))

    def _save(self, task: Task) -> None:
        self.conn.execute("UPDATE task_documents SET body = ? WHERE id = ?", (self._to_document(task), task.id))

    # --- 공개 메서드 ---

    def add(self, title: str, tags: Iterable[str] = (), due: date | None = None) -> Task:
        draft = Task(id=0, title=title, tags=list(tags), due=due)  # 검증(빈 제목 등)은 Task 가 한다
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO task_documents (body) VALUES (?)", (self._to_document(draft),)
            )
        return Task(id=cursor.lastrowid, title=draft.title, tags=draft.tags, due=draft.due)

    def get(self, task_id: int) -> Task:
        row = self.conn.execute("SELECT body FROM task_documents WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise TaskNotFoundError(task_id)
        return self._to_task(task_id, row[0])

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        if task.done:
            raise ValueError(f"할 일 #{task_id} 은(는) 이미 완료되었습니다")
        task.done = True
        task.version += 1
        with self.conn:
            self._save(task)
        return task

    def remove(self, task_id: int) -> Task:
        task = self.get(task_id)
        with self.conn:
            self.conn.execute("DELETE FROM task_documents WHERE id = ?", (task_id,))
        return task

    def all(self) -> list[Task]:
        rows = self.conn.execute("SELECT id, body FROM task_documents ORDER BY id").fetchall()
        return [self._to_task(task_id, body) for task_id, body in rows]

    def open_tasks(self) -> list[Task]:
        rows = self.conn.execute(
            "SELECT id, body FROM task_documents WHERE json_extract(body, '$.done') = 0 ORDER BY id"
        ).fetchall()
        return [self._to_task(task_id, body) for task_id, body in rows]

    def by_tag(self, tag: str) -> list[Task]:
        rows = self.conn.execute(
            """
            SELECT task_documents.id, task_documents.body
            FROM task_documents, json_each(task_documents.body, '$.tags')
            WHERE json_each.value = ?
            ORDER BY task_documents.id
            """,
            (tag.strip(),),
        ).fetchall()
        return [self._to_task(task_id, body) for task_id, body in rows]

    def tag_counts(self) -> dict[str, int]:
        rows = self.conn.execute(
            """
            SELECT json_each.value, COUNT(*)
            FROM task_documents, json_each(task_documents.body, '$.tags')
            GROUP BY json_each.value
            ORDER BY json_each.value
            """
        ).fetchall()
        return {name: count for name, count in rows}

    def __len__(self) -> int:
        (count,) = self.conn.execute("SELECT COUNT(*) FROM task_documents").fetchone()
        return count
