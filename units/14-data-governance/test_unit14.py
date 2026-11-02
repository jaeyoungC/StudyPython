"""14단원 테스트 뼈대. 실행: pytest units/14-data-governance

이 단원은 ◐ (테스트 뼈대만 제공) 입니다. 각 테스트의 독스트링이 **기대하는 동작**이고, 본문은 아직 `pytest.fail` 입니다.
독스트링을 읽고 → 시작 코드의 TODO 를 채우고 → `pytest.fail` 줄을 지우고 실제 단언(assert)으로 바꾸세요.
이전 단원의 테스트 파일들이 좋은 참고가 됩니다. 픽스처는 미리 만들어 두었습니다.
"""

import sqlite3
from datetime import datetime, timedelta

import pytest

from todo.audit import AuditLog
from todo.migrate import current_version
from todo.pii import Sensitivity, classify, redact
from todo.retention import expired_task_ids, purge_completed
from todo.storage_sqlite import SqliteTaskStore
from todo.vectors import cosine_similarity, dot, top_k


class FakeClock:
    """진짜처럼 동작하지만 우리가 시간을 정하는 가짜(fake) 시계. `now` 를 바꿔 시간을 흐르게 한다."""

    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture
def clock():
    return FakeClock(datetime(2026, 3, 1, 9, 0, 0))


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def store(conn, clock):
    s = SqliteTaskStore(conn, clock=clock)
    s.init_schema()
    return s


@pytest.fixture
def audit(conn, clock):
    return AuditLog(conn, clock=clock)


# --- 004 마이그레이션 --------------------------------------------------------------------


def test_migration_004_adds_completed_at_audit_log_and_fts(store, conn):
    """init_schema() 뒤 user_version 은 4 이고, tasks 에 completed_at 열이, 테이블 목록에 audit_log 와 tasks_fts 가 있다."""
    pytest.fail("아직 구현하지 않음")


def test_complete_records_completed_at_from_injected_clock(store, clock):
    """complete(1) 뒤 tasks.completed_at 은 clock() 의 ISO 문자열이고, 미완료 할 일의 completed_at 은 NULL 이다."""
    pytest.fail("아직 구현하지 않음")


# --- 감사 로그 ------------------------------------------------------------------------------


def test_audit_record_and_entries(audit, clock):
    """record("remove", actor="cli", task_id=3, detail="제목: 치과") 뒤 entries() 는 at(시계 값의 ISO 문자열)·actor·action·task_id·detail 이 든 딕셔너리 하나를 돌려준다."""
    pytest.fail("아직 구현하지 않음")


def test_audit_entries_filter_by_task_id_and_keep_order(audit, clock):
    """task 1, 2, 1 순으로 세 건 기록하면 entries(task_id=1) 은 두 건을 기록한 순서대로 돌려준다."""
    pytest.fail("아직 구현하지 않음")


def test_audit_log_survives_task_removal(store, audit):
    """할 일을 remove 한 뒤에도 그 task_id 의 감사 기록은 남아 있다 (FK CASCADE 로 지워지면 안 된다)."""
    pytest.fail("아직 구현하지 않음")


def test_audit_log_rejects_update_and_delete(audit, conn):
    """(선택 — 트리거를 만들었다면) audit_log 행을 UPDATE 하거나 DELETE 하면 sqlite3.IntegrityError 혹은 OperationalError 가 난다."""
    pytest.fail("아직 구현하지 않음")


# --- 보존 기간과 삭제 ---------------------------------------------------------------------------


def test_expired_task_ids_lists_only_old_completed_tasks(store, clock):
    """할 일 셋: 1 은 40일 전 완료, 2 는 5일 전 완료, 3 은 미완료. keep_for=30일이면 expired_task_ids 는 [1] 이다.
    (완료 시각은 clock.now 를 바꿔 가며 complete 를 불러 만든다.)"""
    pytest.fail("아직 구현하지 않음")


def test_purge_dry_run_deletes_nothing(store, audit, clock):
    """dry_run=True 는 지울 id 목록만 돌려주고 len(store) 와 audit.entries() 는 그대로다."""
    pytest.fail("아직 구현하지 않음")


def test_purge_deletes_and_writes_one_audit_entry_per_task(store, audit, clock):
    """dry_run=False 면 만료된 할 일이 사라지고, 지운 할 일마다 action="purge" 인 감사 기록이 하나씩 생긴다. 최근 완료·미완료는 남는다."""
    pytest.fail("아직 구현하지 않음")


def test_purge_is_idempotent(store, audit, clock):
    """같은 조건으로 두 번 purge 하면 두 번째는 [] 를 돌려주고 감사 기록도 늘지 않는다."""
    pytest.fail("아직 구현하지 않음")


# --- 개인정보 분류와 가림 -------------------------------------------------------------------------


def test_every_column_has_a_sensitivity():
    """tasks(id, title, done, version, due, completed_at) 와 audit_log(at, actor, action, task_id, detail) 의 모든 열이 FIELD_SENSITIVITY 에 있고, classify() 가 Sensitivity 를 돌려준다."""
    pytest.fail("아직 구현하지 않음")


def test_unknown_field_is_treated_as_secret():
    """classify("tasks.no_such_column") 은 Sensitivity.SECRET 이다 — 모르는 것은 가장 엄격하게."""
    pytest.fail("아직 구현하지 않음")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("민수에게 010-1234-5678 로 전화", "민수에게 [phone] 로 전화"),
        ("a.b+c@example.com 에 답장", "[email] 에 답장"),
        ("01012345678 과 x@y.kr 둘 다", "[phone] 과 [email] 둘 다"),
        ("개인정보 없음", "개인정보 없음"),
    ],
)
def test_redact_masks_phone_and_email(text, expected):
    """redact(text) == expected. 원본 문자열은 바뀌지 않는다."""
    pytest.fail("아직 구현하지 않음")


# --- 전문 검색 (FTS5) ------------------------------------------------------------------------------


def test_search_finds_by_word_in_title(store):
    """"SQL 공부", "산책", "SQL 인덱스 복습" 을 넣고 search("SQL") 하면 id 1 과 3 이 (순서 무관) 나오고 2 는 안 나온다."""
    pytest.fail("아직 구현하지 않음")


def test_search_reflects_rename_and_remove(store):
    """rename 으로 제목에서 단어가 빠지면 더 이상 검색되지 않고, remove 된 할 일도 검색되지 않는다 (트리거가 색인을 따라가야 한다)."""
    pytest.fail("아직 구현하지 않음")


def test_search_empty_or_whitespace_returns_empty_list(store):
    """search("") 과 search("   ") 은 [] 이고 예외를 내지 않는다."""
    pytest.fail("아직 구현하지 않음")


def test_search_with_quotes_does_not_crash(store):
    """search('"') 나 search("a OR") 처럼 FTS5 문법에 걸리는 입력도 예외 없이 리스트를 돌려준다 (구절 검색으로 감싸거나 걸러서)."""
    pytest.fail("아직 구현하지 않음")


# --- 벡터 검색 개념 --------------------------------------------------------------------------------


def test_dot_product_and_length_mismatch():
    """dot([1, 2, 3], [4, 5, 6]) == 32 이고, 길이가 다르면 ValueError."""
    pytest.fail("아직 구현하지 않음")


def test_cosine_similarity_known_values():
    """같은 방향 [1, 0]·[2, 0] 은 1.0, 직교 [1, 0]·[0, 1] 은 0.0, 반대 [1, 0]·[-1, 0] 은 -1.0 (pytest.approx 사용). 영벡터는 ValueError."""
    pytest.fail("아직 구현하지 않음")


def test_top_k_returns_most_similar_first():
    """items = [("산책", [1, 0]), ("SQL", [0, 1]), ("달리기", [0.9, 0.1])], query [1, 0], k=2 → ids 가 ["산책", "달리기"] 이고 유사도는 내림차순."""
    pytest.fail("아직 구현하지 않음")


def test_top_k_with_k_larger_than_items_returns_all():
    """항목이 2개인데 k=5 면 2개를 돌려준다."""
    pytest.fail("아직 구현하지 않음")
