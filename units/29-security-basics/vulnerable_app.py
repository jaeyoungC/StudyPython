"""29단원: 보안 기초 — 일부러 취약하게 쓴 모듈. 이 파일을 '고치는' 것이 과제입니다.

이 파일에는 적어도 여섯 가지 문제가 있습니다. 전부 찾아 README 의 체크리스트와 대조하고,
test_unit29.py 의 뼈대를 채워 "고쳐졌음"을 테스트로 증명하세요. 함수 이름과 인자는 유지합니다(테스트가 그 이름을 씁니다).

주의: 실제 비밀값을 이 저장소에 넣지 마세요. 아래 값은 가짜입니다.
"""

from __future__ import annotations

import hashlib
import random
import sqlite3
from pathlib import Path

# 문제 1: 하드코딩된 비밀값. 커밋되는 순간 git 역사에 영원히 남는다.
API_SECRET = "sk-live-0123456789abcdef"

EXPORT_DIR = Path("exports")


def init_schema(conn: sqlite3.Connection) -> None:
    """완성되어 있습니다. 수정하지 마세요."""
    with conn:
        conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)")
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")


def find_tasks_by_title(conn: sqlite3.Connection, title: str) -> list[tuple]:
    # 문제 2: 문자열 포매팅으로 만든 SQL. title 에 ' OR '1'='1 이 오면?
    return conn.execute(f"SELECT id, title, done FROM tasks WHERE title = '{title}'").fetchall()


def create_task(conn: sqlite3.Connection, title) -> int:
    # 문제 3: 입력 검증 없음. None, 빈 문자열, 10만 자짜리 제목, 문자열이 아닌 값이 그대로 들어간다.
    cur = conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    conn.commit()
    return cur.lastrowid


def register(conn: sqlite3.Connection, username: str, password: str) -> None:
    # 문제 4: 비밀번호를 평문으로 저장. (18단원에서 해싱을 배웠다. 여기서는 hashlib.scrypt 또는 그때 쓴 라이브러리를 쓴다)
    with conn:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))


def login(conn: sqlite3.Connection, username: str, password: str) -> bool:
    # 문제 2 다시: 인젝션. 문제 4 다시: 평문 비교. 그리고 "사용자 없음"과 "비밀번호 틀림"을 다르게 응답하면 사용자 이름을 추측당한다.
    row = conn.execute(f"SELECT password FROM users WHERE username = '{username}'").fetchone()
    if row is None:
        raise ValueError("no such user")
    return row[0] == password


def make_reset_token() -> str:
    # 문제 5: random 은 예측 가능한 난수다. 보안 토큰에는 secrets 모듈을 쓴다.
    return hashlib.md5(str(random.random()).encode()).hexdigest()


def read_export(filename: str) -> str:
    # 문제 6: 경로 탐색(path traversal). filename 이 "../../.env" 이면?
    return (EXPORT_DIR / filename).read_text(encoding="utf-8")
