"""31단원 테스트. 실행: pytest units/31-logging

로그 출력은 StringIO 에 받아서 JSON 으로 파싱해 검사합니다. 마지막 두 테스트는 pytest 의 caplog 를 씁니다.
"""

import io
import json
import logging
from datetime import date

import pytest

from structured_logging import (
    REDACTED,
    JsonFormatter,
    configure_logging,
    new_request_id,
    redact,
    request_context,
    request_id_var,
)


@pytest.fixture
def log_and_output():
    """독립된 로거와 그 출력 버퍼. 돌려주는 read() 는 지금까지 찍힌 줄들을 dict 리스트로 파싱한다."""
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("unit31.test")
    logger.handlers = [handler]
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    def read() -> list[dict]:
        return [json.loads(line) for line in buffer.getvalue().splitlines()]

    yield logger, read, buffer
    logger.handlers = []


# ---------------------------------------------------------------------------
# JsonFormatter
# ---------------------------------------------------------------------------


def test_each_record_is_one_json_line_with_core_fields(log_and_output):
    logger, read, _ = log_and_output
    logger.info("할 일 추가됨")
    logger.warning("느린 쿼리")

    lines = read()
    assert len(lines) == 2
    assert lines[0]["level"] == "INFO" and lines[0]["message"] == "할 일 추가됨"
    assert lines[1]["level"] == "WARNING" and lines[1]["message"] == "느린 쿼리"
    assert lines[0]["logger"] == "unit31.test"


def test_message_arguments_are_interpolated(log_and_output):
    logger, read, _ = log_and_output
    logger.info("task %d completed by %s", 7, "alice")
    assert read()[0]["message"] == "task 7 completed by alice"


def test_timestamp_is_iso8601_utc(log_and_output):
    logger, read, _ = log_and_output
    logger.info("x")
    ts = read()[0]["ts"]
    assert ts.endswith("+00:00")
    assert "T" in ts


def test_extra_fields_are_included(log_and_output):
    logger, read, _ = log_and_output
    logger.info("completed", extra={"task_id": 3, "duration_ms": 12.5})
    line = read()[0]
    assert line["task_id"] == 3
    assert line["duration_ms"] == 12.5


def test_non_json_values_in_extra_become_strings(log_and_output):
    logger, read, _ = log_and_output
    logger.info("due", extra={"due": date(2026, 11, 2)})
    assert read()[0]["due"] == "2026-11-02"


def test_exception_info_is_included_when_present(log_and_output):
    logger, read, _ = log_and_output
    try:
        {}["missing"]
    except KeyError:
        logger.exception("조회 실패")
    line = read()[0]
    assert "KeyError" in line["exc_info"]
    assert "Traceback" in line["exc_info"]


def test_exc_info_key_is_absent_without_exception(log_and_output):
    logger, read, _ = log_and_output
    logger.info("정상")
    assert "exc_info" not in read()[0]


def test_output_is_not_ascii_escaped(log_and_output):
    logger, _, buffer = log_and_output
    logger.info("한글")
    assert "한글" in buffer.getvalue()  # ensure_ascii=False 가 아니면 \ud55c\uae00 로 찍힌다


# ---------------------------------------------------------------------------
# 요청 id (contextvars)
# ---------------------------------------------------------------------------


def test_request_id_is_null_outside_context(log_and_output):
    logger, read, _ = log_and_output
    logger.info("x")
    assert read()[0]["request_id"] is None


def test_request_id_is_attached_inside_context(log_and_output):
    logger, read, _ = log_and_output
    with request_context("req-123"):
        logger.info("안")
    logger.info("밖")
    lines = read()
    assert lines[0]["request_id"] == "req-123"
    assert lines[1]["request_id"] is None


def test_request_context_generates_an_id_when_none_given():
    with request_context() as rid:
        assert isinstance(rid, str) and len(rid) == 32
        assert request_id_var.get() == rid
    assert request_id_var.get() is None


def test_nested_context_restores_outer_id():
    with request_context("outer"):
        with request_context("inner"):
            assert request_id_var.get() == "inner"
        assert request_id_var.get() == "outer"


def test_context_is_restored_even_if_block_raises():
    with pytest.raises(RuntimeError):
        with request_context("boom"):
            raise RuntimeError
    assert request_id_var.get() is None


def test_new_request_ids_are_unique():
    assert len({new_request_id() for _ in range(100)}) == 100


# ---------------------------------------------------------------------------
# 개인정보 가리기
# ---------------------------------------------------------------------------


def test_redact_masks_sensitive_keys_case_insensitively():
    data = {"user": "alice", "password": "pw", "Authorization": "Bearer x", "count": 3}
    assert redact(data) == {"user": "alice", "password": REDACTED, "Authorization": REDACTED, "count": 3}


def test_redact_walks_nested_dicts_and_lists():
    data = {"items": [{"email": "a@example.com", "id": 1}], "meta": {"token": "t", "ok": True}}
    assert redact(data) == {"items": [{"email": REDACTED, "id": 1}], "meta": {"token": REDACTED, "ok": True}}


def test_redact_does_not_mutate_input():
    data = {"password": "pw", "nested": {"token": "t"}}
    redact(data)
    assert data == {"password": "pw", "nested": {"token": "t"}}


def test_redact_leaves_plain_values_alone():
    assert redact("password") == "password"  # 값이 아니라 키가 기준이다
    assert redact(42) == 42
    assert redact(None) is None


def test_formatter_redacts_extra_fields(log_and_output):
    logger, read, _ = log_and_output
    logger.info("login", extra={"email": "a@example.com", "password": "pw", "user_id": 1})
    line = read()[0]
    assert line["email"] == REDACTED
    assert line["password"] == REDACTED
    assert line["user_id"] == 1


def test_formatter_accepts_custom_sensitive_keys():
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(JsonFormatter(sensitive_keys=frozenset({"ssn"})))
    logger = logging.getLogger("unit31.custom")
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.info("x", extra={"ssn": "123", "email": "visible@example.com"})
    line = json.loads(buffer.getvalue())
    assert line["ssn"] == REDACTED
    assert line["email"] == "visible@example.com"
    logger.handlers = []


# ---------------------------------------------------------------------------
# configure_logging
# ---------------------------------------------------------------------------


def test_configure_logging_installs_json_handler_once():
    buffer = io.StringIO()
    root = configure_logging(level=logging.INFO, stream=buffer)
    configure_logging(level=logging.INFO, stream=buffer)  # 두 번 불러도
    try:
        logging.getLogger("unit31.app").info("한 번만")
        lines = buffer.getvalue().splitlines()
        assert len(lines) == 1  # 핸들러가 중복되면 두 줄이 찍힌다
        assert json.loads(lines[0])["message"] == "한 번만"
    finally:
        for h in list(root.handlers):
            if getattr(h, "_structured", False):
                root.removeHandler(h)


def test_configure_logging_keeps_other_handlers(caplog):
    """pytest 의 caplog 는 루트 로거에 자기 핸들러를 단다. configure_logging 이 그것을 지우면 안 된다."""
    buffer = io.StringIO()
    root = configure_logging(level=logging.INFO, stream=buffer)
    try:
        with caplog.at_level(logging.WARNING):
            logging.getLogger("unit31.app").warning("둘 다 받아야 한다")
        assert "둘 다 받아야 한다" in caplog.text
        assert "둘 다 받아야 한다" in buffer.getvalue()
    finally:
        for h in list(root.handlers):
            if getattr(h, "_structured", False):
                root.removeHandler(h)


def test_caplog_sees_request_id_on_record(caplog):
    """caplog 는 포맷 전의 LogRecord 를 준다. 요청 id 는 포매터가 붙이므로 record 에는 없다 — 그래서 포매터 테스트가 따로 필요하다."""
    with caplog.at_level(logging.INFO), request_context("req-9"):
        logging.getLogger("unit31.app").info("기록")
    record = caplog.records[-1]
    assert record.getMessage() == "기록"
    assert "request_id" not in record.__dict__
    assert request_id_var.get() is None
