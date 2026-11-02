"""12단원: 번호 붙은 SQL 파일로 스키마를 단계적으로 바꾼다.

규칙
- `todo/migrations/NNN_설명.sql` (NNN 은 세 자리 숫자). 번호 순으로 적용한다.
- DB 는 지금 몇 번까지 적용했는지를 `PRAGMA user_version` (SQLite 파일 헤더의 정수 하나) 에 기억한다.
- 파일 하나 = 트랜잭션 하나. 중간에 실패하면 그 파일의 변경과 번호 증가가 모두 되돌아간다 (`_apply` 참고).
- 이미 적용된 파일은 **절대 고치지 않는다**. 바꾸고 싶으면 다음 번호의 새 파일을 만든다.

TODO 는 세 함수: current_version, load_migrations, migrate.  (_apply 와 pending 은 완성되어 있다.)
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
FILENAME = re.compile(r"^(\d{3})_[A-Za-z0-9_]+\.sql$")  # 예: 002_add_due.sql → group(1) == "002"


class MigrationError(Exception):
    """마이그레이션 파일이 잘못되었거나 적용 중 실패했을 때."""


def current_version(conn: sqlite3.Connection) -> int:
    """DB 에 적용된 마지막 마이그레이션 번호. 한 번도 적용하지 않았으면 0.

    힌트: `PRAGMA user_version` 을 SELECT 처럼 실행하면 정수 하나가 든 행이 나온다.
    """
    # TODO
    raise NotImplementedError


def load_migrations(directory: Path = MIGRATIONS_DIR) -> list[tuple[int, Path]]:
    """폴더 안의 마이그레이션 파일을 (번호, 경로) 로 **번호 오름차순** 정렬해 돌려준다.

    - 이름이 FILENAME 패턴에 맞지 않는 파일(README, .sql.bak 등)은 무시한다.
    - 같은 번호가 둘이면 MigrationError (두 사람이 같은 번호를 쓰는 사고는 PR 에서 잡아야 한다).
    힌트: Path.iterdir(), FILENAME.match(path.name), int(match.group(1)), sorted(dict.items())
    """
    # TODO
    raise NotImplementedError


def pending(conn: sqlite3.Connection, directory: Path = MIGRATIONS_DIR) -> list[tuple[int, Path]]:
    """아직 적용되지 않은(번호가 current_version 보다 큰) 마이그레이션만."""
    version = current_version(conn)
    return [(number, path) for number, path in load_migrations(directory) if number > version]


def _apply(conn: sqlite3.Connection, number: int, sql: str) -> None:
    """SQL 파일 하나를 트랜잭션 하나로 적용하고 user_version 을 올린다. 중간에 실패하면 전부 되돌린다.

    executescript 는 여러 문장을 실행할 수 있지만 자동으로 트랜잭션으로 묶어 주지는 않는다. 그래서 스크립트 앞뒤에
    BEGIN / COMMIT 을 직접 붙이고, 실패하면 ROLLBACK 한다. PRAGMA user_version 도 트랜잭션 안에서 되돌려진다.
    """
    script = f"BEGIN;\n{sql}\nPRAGMA user_version = {number};\nCOMMIT;"
    try:
        conn.executescript(script)
    except sqlite3.Error as error:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise MigrationError(f"마이그레이션 {number:03d} 적용 실패: {error}") from error


def migrate(
    conn: sqlite3.Connection, directory: Path = MIGRATIONS_DIR, target: int | None = None
) -> list[int]:
    """pending 마이그레이션을 번호 순으로 적용하고, 적용한 번호 목록을 돌려준다.

    - target 이 주어지면 그 번호까지만 적용한다 (테스트에서 "1번까지만 적용된 옛날 DB" 를 만들 때 쓴다).
    - 적용할 것이 없으면 [] (여러 번 불러도 안전해야 한다 — init_schema() 가 매번 부른다).
    """
    # TODO
    raise NotImplementedError
