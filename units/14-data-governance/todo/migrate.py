"""번호 붙은 SQL 파일로 스키마를 단계적으로 바꾼다 (12단원 완성본)."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
FILENAME = re.compile(r"^(\d{3})_[A-Za-z0-9_]+\.sql$")


class MigrationError(Exception):
    """마이그레이션 파일이 잘못되었거나 적용 중 실패했을 때."""


def current_version(conn: sqlite3.Connection) -> int:
    (version,) = conn.execute("PRAGMA user_version").fetchone()
    return version


def load_migrations(directory: Path = MIGRATIONS_DIR) -> list[tuple[int, Path]]:
    found: dict[int, Path] = {}
    for path in Path(directory).iterdir():
        match = FILENAME.match(path.name)
        if not match:
            continue
        number = int(match.group(1))
        if number in found:
            raise MigrationError(f"번호 {number:03d} 가 중복됩니다: {found[number].name}, {path.name}")
        found[number] = path
    return sorted(found.items())


def pending(conn: sqlite3.Connection, directory: Path = MIGRATIONS_DIR) -> list[tuple[int, Path]]:
    version = current_version(conn)
    return [(number, path) for number, path in load_migrations(directory) if number > version]


def _apply(conn: sqlite3.Connection, number: int, sql: str) -> None:
    """SQL 파일 하나를 트랜잭션 하나로 적용하고 user_version 을 올린다. 중간에 실패하면 전부 되돌린다."""
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
    applied: list[int] = []
    for number, path in pending(conn, directory):
        if target is not None and number > target:
            break
        _apply(conn, number, path.read_text(encoding="utf-8"))
        applied.append(number)
    return applied
