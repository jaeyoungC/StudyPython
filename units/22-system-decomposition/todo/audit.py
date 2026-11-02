"""감사 로그(audit log, 14단원): 누가(여기서는 무엇이) 언제 무엇을 했는지 기록한다."""

from __future__ import annotations

import sqlite3
from datetime import datetime


def log_action(conn: sqlite3.Connection, action: str, task_id: int | None, at: datetime, detail: str = "") -> None:
    conn.execute(
        "INSERT INTO audit_log (at, action, task_id, detail) VALUES (?, ?, ?, ?)",
        (at.isoformat(timespec="seconds"), action, task_id, detail),
    )


def audit_entries(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT id, at, action, task_id, detail FROM audit_log ORDER BY id").fetchall()
    return [dict(zip(("id", "at", "action", "task_id", "detail"), row)) for row in rows]
