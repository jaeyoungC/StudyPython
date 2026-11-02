"""13단원: 문서형(document) 저장소 — 할 일 하나 = JSON 문서 하나.

관계형 저장소(storage_sqlite.py)와 **같은 메서드 이름·같은 동작**을 제공하되, 테이블은 하나뿐이고
제목·완료 여부·태그·마감일이 전부 `body` 열의 JSON 안에 들어 있다. MongoDB 같은 문서형 DB 의 축소판이다.
(SQLite 안에서 흉내 내는 이유: 새 DB 를 설치하지 않고도 "조회 방식의 차이"를 같은 테스트로 비교하기 위해.)

문서 모양: {"title": "...", "done": false, "tags": ["a", "b"], "version": 1, "due": null}

SQLite 의 JSON 함수:
  json_extract(body, '$.done')          문서에서 값 하나 꺼내기
  json_each(body, '$.tags')             배열을 행으로 펼치기 (FROM 절에 테이블처럼 쓴다, 열 이름은 value)
  json_valid(body)                      올바른 JSON 인지 — CHECK 제약에 쓴다
참고: https://sqlite.org/json1.html

TODO 는 add, get, complete, open_tasks, by_tag 다섯 개. 나머지는 완성되어 있으니 패턴을 보고 따라 하자.
"""

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
        """문서 하나를 INSERT 하고 DB 가 매긴 id 로 Task 를 돌려준다.

        힌트: 먼저 `Task(id=0, title=title, tags=list(tags), due=due)` 로 임시 Task 를 만들면 빈 제목 검사와
        태그 정리를 Task 가 해 준다. `_to_document` 로 문자열을 만들어 넣고, lastrowid 로 진짜 Task 를 만든다.
        """
        # TODO
        raise NotImplementedError

    def get(self, task_id: int) -> Task:
        """body 를 읽어 `_to_task` 로 바꾼다. 없으면 TaskNotFoundError."""
        # TODO
        raise NotImplementedError

    def complete(self, task_id: int) -> Task:
        """문서형의 갱신은 "읽기 → 파이썬에서 고치기 → 문서 전체 다시 쓰기" 다. 이미 완료면 ValueError.

        done 을 True 로, version 을 +1 한 뒤 `_save`. (관계형의 `UPDATE tasks SET done = 1` 과 비교해 보라 —
        문서형은 열 하나를 바꾸기 위해 문서 전체를 다시 쓴다.)
        """
        # TODO
        raise NotImplementedError

    def remove(self, task_id: int) -> Task:
        task = self.get(task_id)
        with self.conn:
            self.conn.execute("DELETE FROM task_documents WHERE id = ?", (task_id,))
        return task

    def all(self) -> list[Task]:
        rows = self.conn.execute("SELECT id, body FROM task_documents ORDER BY id").fetchall()
        return [self._to_task(task_id, body) for task_id, body in rows]

    def open_tasks(self) -> list[Task]:
        """done 이 false 인 문서만 id 순으로. 힌트: WHERE json_extract(body, '$.done') = 0  (JSON false 는 0 으로 비교된다)"""
        # TODO
        raise NotImplementedError

    def by_tag(self, tag: str) -> list[Task]:
        """태그가 붙은 문서만 id 순으로. 연결 테이블이 없으니 JSON 배열을 펼쳐서 찾아야 한다.

        힌트: FROM task_documents, json_each(task_documents.body, '$.tags') WHERE json_each.value = ?
        (tag_counts 가 같은 기법을 쓴다.) 10단원처럼 EXPLAIN QUERY PLAN 을 찍어 보면 어떤 모양일까?
        """
        # TODO
        raise NotImplementedError

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
