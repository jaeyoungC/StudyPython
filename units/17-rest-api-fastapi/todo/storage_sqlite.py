"""SQLite 저장소 (08~14단원 완성본).

- 스키마는 migrations/*.sql 을 번호 순서로 적용하고 PRAGMA user_version 으로 어디까지 적용했는지 기억한다.
- 태그는 tags / task_tags 테이블(N:M), 검색은 FTS5 가상 테이블 tasks_fts, 변경은 audit_log 에 남긴다.
- 테스트는 sqlite3.connect(":memory:") 로 쓴다.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Iterable
from datetime import date, datetime
from pathlib import Path

from .audit import log_action
from .models import Task, TaskNotFoundError

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def migrate(conn: sqlite3.Connection) -> int:
    """아직 적용하지 않은 마이그레이션을 순서대로 적용하고 최종 버전을 돌려준다."""
    current = conn.execute("PRAGMA user_version").fetchone()[0]
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        number = int(path.name.split("_", 1)[0])
        if number <= current:
            continue
        with conn:
            conn.executescript(path.read_text(encoding="utf-8"))
            conn.execute(f"PRAGMA user_version = {number}")
        current = number
    return current


class SqliteTaskStore:
    def __init__(self, conn: sqlite3.Connection, clock: Callable[[], datetime] = datetime.now) -> None:
        self.conn = conn
        self.clock = clock
        self.conn.execute("PRAGMA foreign_keys = ON")

    def init_schema(self) -> None:
        migrate(self.conn)

    # -- 읽기 ---------------------------------------------------------------

    def _row_to_task(self, row: tuple) -> Task:
        task_id, title, done, due = row
        tags = [
            r[0]
            for r in self.conn.execute(
                "SELECT t.name FROM tags t JOIN task_tags tt ON tt.tag_id = t.id "
                "WHERE tt.task_id = ? ORDER BY t.name",
                (task_id,),
            )
        ]
        return Task(id=task_id, title=title, done=bool(done), tags=tags, due=date.fromisoformat(due) if due else None)

    def _select(self, where: str = "", params: tuple = ()) -> list[Task]:
        rows = self.conn.execute(f"SELECT id, title, done, due FROM tasks {where} ORDER BY id", params).fetchall()
        return [self._row_to_task(r) for r in rows]

    def get(self, task_id: int) -> Task:
        found = self._select("WHERE id = ?", (task_id,))
        if not found:
            raise TaskNotFoundError(f"할 일 #{task_id} 이(가) 없습니다")
        return found[0]

    def all(self) -> list[Task]:
        return self._select()

    def open_tasks(self) -> list[Task]:
        return self._select("WHERE done = 0")

    def by_tag(self, tag: str) -> list[Task]:
        return self._select(
            "WHERE id IN (SELECT tt.task_id FROM task_tags tt JOIN tags t ON t.id = tt.tag_id WHERE t.name = ?)",
            (tag,),
        )

    def search(self, text: str) -> list[Task]:
        """FTS5 전문 검색. 따옴표로 감싸 구문 검색 문법 오류를 피한다."""
        query = '"' + text.replace('"', '""') + '"'
        rows = self.conn.execute(
            "SELECT t.id, t.title, t.done, t.due FROM tasks_fts f JOIN tasks t ON t.id = f.rowid "
            "WHERE tasks_fts MATCH ? ORDER BY rank",
            (query,),
        ).fetchall()
        return [self._row_to_task(r) for r in rows]

    def __len__(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

    # -- 쓰기 (각 메서드가 하나의 트랜잭션) -----------------------------------

    def add(self, title: str, tags: Iterable[str] = (), due: date | None = None) -> Task:
        draft = Task(id=0, title=title, tags=list(tags), due=due)  # 검증(공백 제거, 빈 제목)
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO tasks (title, done, due) VALUES (?, 0, ?)",
                (draft.title, draft.due.isoformat() if draft.due else None),
            )
            task_id = cur.lastrowid
            for tag in draft.tags:
                self.conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
                self.conn.execute(
                    "INSERT OR IGNORE INTO task_tags (task_id, tag_id) SELECT ?, id FROM tags WHERE name = ?",
                    (task_id, tag),
                )
            log_action(self.conn, "add", task_id, self.clock(), draft.title)
        return self.get(task_id)

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        if task.done:
            raise ValueError(f"할 일 #{task_id} 은(는) 이미 완료되었습니다")
        with self.conn:
            self.conn.execute("UPDATE tasks SET done = 1, version = version + 1 WHERE id = ?", (task_id,))
            log_action(self.conn, "complete", task_id, self.clock())
        return self.get(task_id)

    def remove(self, task_id: int) -> Task:
        task = self.get(task_id)
        with self.conn:
            self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            log_action(self.conn, "remove", task_id, self.clock(), task.title)
        return task

    def move_tag(self, task_id: int, from_tag: str, to_tag: str) -> Task:
        """태그 하나를 다른 태그로 바꾼다. 중간에 실패하면 전부 되돌린다 (11단원)."""
        self.get(task_id)
        with self.conn:
            self.conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (to_tag,))
            self.conn.execute(
                "DELETE FROM task_tags WHERE task_id = ? AND tag_id = (SELECT id FROM tags WHERE name = ?)",
                (task_id, from_tag),
            )
            self.conn.execute(
                "INSERT OR IGNORE INTO task_tags (task_id, tag_id) SELECT ?, id FROM tags WHERE name = ?",
                (task_id, to_tag),
            )
            log_action(self.conn, "move_tag", task_id, self.clock(), f"{from_tag} -> {to_tag}")
        return self.get(task_id)
