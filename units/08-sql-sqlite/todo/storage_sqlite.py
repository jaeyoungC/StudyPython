"""08단원: SQLite 저장소.

TaskList(models.py)와 같은 메서드를 제공하되, 데이터를 메모리 리스트가 아니라 SQLite
테이블에 둔다. 생성자는 **열린 연결(connection)** 을 받는다. 파일을 열지 않으므로
테스트는 `sqlite3.connect(":memory:")` 로 빈 DB 를 넘길 수 있다.

규칙
- SQL 에 값을 넣을 때는 반드시 `?` 자리표시자(placeholder)를 쓴다. f-string 금지.
- 쓰기(INSERT/UPDATE/DELETE) 뒤에는 `self.conn.commit()` 을 부른다. (왜 필요한지는 11단원에서
  트랜잭션을 배우며 자세히 다룬다. 지금은 "commit 하지 않은 변경은 다른 연결에서 보이지 않고,
  연결이 닫히면 사라진다" 정도로 기억하자.)
- 없는 id 는 TaskNotFoundError, 빈 제목·중복 완료는 ValueError. TaskList 와 똑같다.
"""

from __future__ import annotations

import sqlite3

from .models import Task, TaskNotFoundError

# 테이블 정의. 제약(constraint)은 "잘못된 데이터가 들어오는 길을 DB 차원에서 막는" 장치다.
#   PRIMARY KEY : 행을 유일하게 식별. INTEGER PRIMARY KEY 는 비우고 INSERT 하면 DB 가 번호를 매긴다.
#   NOT NULL    : 비어 있으면(NULL) 거부
#   CHECK       : 조건이 거짓이면 거부
SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id    INTEGER PRIMARY KEY,
    title TEXT    NOT NULL CHECK (length(trim(title)) > 0),
    done  INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
);
"""

# SELECT 에서 항상 같은 순서로 열을 읽기 위한 상수. `SELECT *` 는 열 순서가 바뀌면 조용히 깨진다.
SELECT_COLUMNS = "id, title, done"


def _row_to_task(row: tuple) -> Task:
    """(id, title, done) 튜플 한 줄을 Task 로 바꾼다. SQLite 에는 bool 이 없어 0/1 로 저장된다."""
    task_id, title, done = row
    return Task(id=task_id, title=title, done=bool(done))


class SqliteTaskStore:
    """할 일을 SQLite 테이블 `tasks` 에 저장한다."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def init_schema(self) -> None:
        """테이블이 없으면 만든다. 여러 번 불러도 안전해야 한다 (IF NOT EXISTS)."""
        # TODO: SCHEMA 를 실행한다. 힌트: 여러 문장을 한 번에 실행하는 메서드가 있다.
        raise NotImplementedError

    def add(self, title: str) -> Task:
        """할 일을 INSERT 하고, DB 가 매긴 id 로 Task 를 만들어 돌려준다.

        - 제목 앞뒤 공백은 제거한다.
        - 빈 제목은 ValueError. (CHECK 제약이 sqlite3.IntegrityError 를 던지므로
          그것을 잡아 ValueError 로 바꾸면 TaskList 와 같은 인터페이스가 된다. `raise ... from` 을 쓰자.)
        - 힌트: cursor.lastrowid
        """
        # TODO
        raise NotImplementedError

    def get(self, task_id: int) -> Task:
        """id 로 한 건을 SELECT 한다. 없으면 TaskNotFoundError. 힌트: fetchone() 은 없으면 None."""
        # TODO
        raise NotImplementedError

    def complete(self, task_id: int) -> Task:
        """done 을 1 로 UPDATE 하고 바뀐 Task 를 돌려준다. 없으면 TaskNotFoundError, 이미 완료면 ValueError."""
        # TODO
        raise NotImplementedError

    def remove(self, task_id: int) -> Task:
        """행을 DELETE 하고 지운 Task 를 돌려준다. 없으면 TaskNotFoundError."""
        # TODO
        raise NotImplementedError

    def all(self) -> list[Task]:
        """모든 할 일을 id 순으로. ORDER BY 를 빼먹으면 순서는 보장되지 않는다."""
        # TODO
        raise NotImplementedError

    def open_tasks(self) -> list[Task]:
        """done = 0 인 할 일만 id 순으로."""
        # TODO
        raise NotImplementedError

    def __len__(self) -> int:
        """할 일 개수. 전부 읽어 len() 하지 말고 COUNT(*) 를 쓰자."""
        # TODO
        raise NotImplementedError
