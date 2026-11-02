"""백업과 복구 (12단원 완성본). SQLite 의 온라인 백업 API(`Connection.backup`)를 쓴다."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def backup_to(conn: sqlite3.Connection, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dest = sqlite3.connect(path)
    try:
        conn.backup(dest)
    finally:
        dest.close()
    return path


def restore_from(path: Path, conn: sqlite3.Connection) -> None:
    src = sqlite3.connect(Path(path))
    try:
        src.backup(conn)
    finally:
        src.close()
