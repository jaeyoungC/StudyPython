"""SQL 인젝션(SQL injection) 시연. 수정할 TODO 는 없고, 읽고 실행해 보는 파일입니다.

실행: python units/08-sql-sqlite/injection_demo.py

같은 "제목으로 검색" 기능을 두 가지로 구현했습니다.
- find_by_title_unsafe : f-string 으로 SQL 문자열을 조립한다. 사용자 입력이 SQL 문법의 일부가 된다.
- find_by_title_safe   : `?` 자리표시자(placeholder)를 쓴다. 입력은 끝까지 "값"으로만 다뤄진다.
"""

from __future__ import annotations

import sqlite3


def find_by_title_unsafe(conn: sqlite3.Connection, title: str) -> list[tuple]:
    """절대 이렇게 쓰지 마세요. 시연용입니다."""
    sql = f"SELECT id, title FROM tasks WHERE title = '{title}'"
    return conn.execute(sql).fetchall()


def find_by_title_safe(conn: sqlite3.Connection, title: str) -> list[tuple]:
    """올바른 방법: 값은 `?` 로 넘긴다. 드라이버가 값과 문법을 분리해서 보낸다."""
    return conn.execute("SELECT id, title FROM tasks WHERE title = ?", (title,)).fetchall()


def make_demo_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL)")
    conn.executemany(
        "INSERT INTO tasks (title) VALUES (?)",
        [("월급 명세서 확인",), ("비밀 프로젝트 X 회의",), ("치과 예약",)],
    )
    conn.commit()
    return conn


if __name__ == "__main__":
    conn = make_demo_db()
    attacker_input = "' OR '1'='1"
    print("입력:", repr(attacker_input))
    print("unsafe →", find_by_title_unsafe(conn, attacker_input))  # 조건이 항상 참이 되어 전부 유출
    print("safe   →", find_by_title_safe(conn, attacker_input))  # 그런 제목은 없으니 []
    print()
    print("unsafe 가 실제로 실행한 SQL:")
    print(f"  SELECT id, title FROM tasks WHERE title = '{attacker_input}'")
