"""14단원: 보존 기간(retention)과 삭제 — 데이터 수명주기(lifecycle)의 마지막 단계.

"완료한 지 N 일이 지난 할 일은 지운다" 같은 규칙을 코드로 적고, 지울 때 감사 로그를 남긴다.
지우는 코드는 반드시 **무엇을 지울지 먼저 보여 주는(dry run)** 길이 있어야 한다.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from .audit import AuditLog
from .storage_sqlite import SqliteTaskStore


def expired_task_ids(store: SqliteTaskStore, now: datetime, keep_for: timedelta) -> list[int]:
    """completed_at 이 (now - keep_for) 보다 이전인 완료 할 일의 id 목록 (오름차순). 아무것도 지우지 않는다."""
    # TODO
    raise NotImplementedError


def purge_completed(
    store: SqliteTaskStore, audit: AuditLog, now: datetime, keep_for: timedelta, dry_run: bool = True
) -> list[int]:
    """expired_task_ids 를 지우고 각각 audit.record("purge", ...) 를 남긴다. dry_run=True 면 지우지 않고 목록만 돌려준다."""
    # TODO
    raise NotImplementedError
