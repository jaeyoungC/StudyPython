"""09단원: SQLite 저장소에 태그(N:M) 를 더한다.

08단원에서 만든 부분은 완성되어 있다. 이번 단원의 TODO 는 네 군데:
  1. SCHEMA 에 `tags`, `task_tags` 테이블 추가
  2. `_tags_of` — 한 할 일에 붙은 태그 이름 목록 (JOIN)
  3. `add(title, tags)` — 태그를 tags 테이블에 넣고(이미 있으면 재사용) task_tags 로 연결
  4. `by_tag`, `tag_counts` — JOIN 으로 거르기, GROUP BY 로 세기

태그 이름의 표준화(공백 제거·중복 제거·정렬)는 `models.normalize_tags` 가 맡는다. 저장소는 그 결과를 믿고 저장만 한다.
"""

from __future__ import annotations

import sqlite3
from typing import Iterable

from .models import Task, TaskNotFoundError, normalize_tags

# 접근 패턴(access pattern)을 먼저 적고 스키마를 정했다 (README 참고):
#   A. 할 일 하나의 태그를 보여 준다            → task_tags WHERE task_id = ?
#   B. 태그 하나로 할 일을 거른다               → task_tags WHERE tag_id = ?  (10단원에서 인덱스)
#   C. 태그별 할 일 개수를 센다                 → GROUP BY tag_id
#   D. 할 일을 지우면 연결도 함께 사라져야 한다 → FOREIGN KEY ... ON DELETE CASCADE
SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id    INTEGER PRIMARY KEY,
    title TEXT    NOT NULL CHECK (length(trim(title)) > 0),
    done  INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
);

-- TODO: tags 테이블 — id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE (빈 이름은 CHECK 로 금지)

-- TODO: task_tags 연결 테이블 —
--   task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
--   tag_id  INTEGER NOT NULL REFERENCES tags(id)  ON DELETE CASCADE,
--   PRIMARY KEY (task_id, tag_id)      ← 같은 할 일에 같은 태그를 두 번 붙일 수 없다
"""

SELECT_COLUMNS = "id, title, done"


class SqliteTaskStore:
    """할 일을 `tasks`, 태그를 `tags`, 둘의 관계를 `task_tags` 에 저장한다."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        # SQLite 는 외래 키(foreign key) 검사를 기본으로 꺼 둔다. 연결마다 켜 줘야 한다.
        self.conn.execute("PRAGMA foreign_keys = ON")

    def init_schema(self) -> None:
        self.conn.executescript(SCHEMA)

    # --- 내부 도우미 ---------------------------------------------------------

    def _row_to_task(self, row: tuple) -> Task:
        """(id, title, done) 한 줄 + 그 할 일의 태그 → Task."""
        task_id, title, done = row
        return Task(id=task_id, title=title, done=bool(done), tags=self._tags_of(task_id))

    def _tags_of(self, task_id: int) -> list[str]:
        """할 일 하나에 붙은 태그 이름들을 이름 순으로 돌려준다. (접근 패턴 A)

        힌트: task_tags 와 tags 를 JOIN 하고 WHERE task_tags.task_id = ? ORDER BY tags.name
        """
        # TODO
        raise NotImplementedError

    def _attach_tag(self, task_id: int, tag: str) -> None:
        """태그 이름을 tags 에 넣고(이미 있으면 그대로 두고) task_tags 에 연결 행을 추가한다.

        힌트: `INSERT OR IGNORE INTO tags (name) VALUES (?)` 뒤에 `SELECT id FROM tags WHERE name = ?` 로 id 를 얻는다.
        """
        # TODO
        raise NotImplementedError

    # --- 공개 메서드 ---------------------------------------------------------

    def add(self, title: str, tags: Iterable[str] = ()) -> Task:
        """할 일을 INSERT 하고 태그를 연결한 뒤 Task 를 돌려준다.

        - 빈 제목은 ValueError (08단원과 같음), 이때 태그도 저장되면 안 된다.
        - 태그는 normalize_tags 로 정리한 뒤 `_attach_tag` 로 하나씩 연결한다.
        - 마지막에 한 번만 commit 한다.
        """
        # TODO
        raise NotImplementedError

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
        """tasks 행만 지운다. task_tags 의 연결 행은 ON DELETE CASCADE 가 지워 준다 (접근 패턴 D)."""
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
        """주어진 태그가 붙은 할 일을 id 순으로. 없는 태그면 빈 리스트. (접근 패턴 B)

        힌트: tasks ← task_tags ← tags 세 테이블을 JOIN 하고 WHERE tags.name = ?
        """
        # TODO
        raise NotImplementedError

    def tag_counts(self) -> dict[str, int]:
        """{태그 이름: 붙은 할 일 수}. 어떤 할 일에도 붙지 않은 태그는 포함하지 않는다. (접근 패턴 C)

        힌트: GROUP BY 와 COUNT(). 결과를 딕셔너리로 바꾼다.
        """
        # TODO
        raise NotImplementedError

    def __len__(self) -> int:
        (count,) = self.conn.execute("SELECT COUNT(*) FROM tasks").fetchone()
        return count
