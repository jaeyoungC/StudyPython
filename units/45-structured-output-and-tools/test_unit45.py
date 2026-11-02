"""45단원 테스트 뼈대. 실행: pytest units/45-structured-output-and-tools

FakeLLM 이 돌려주는 JSON 문자열만 씁니다. 네트워크 없음.
`pytest.fail("아직 구현하지 않음")` 을 실제 검증으로 바꾸세요.
"""

import json
from datetime import date

import pytest

from parse_task import (  # noqa: F401
    ADD_TASK_TOOL,
    CONFIDENCE_THRESHOLD,
    TASK_DRAFT_SCHEMA,
    ClarificationNeeded,
    DraftValidationError,
    FakeLLM,
    TaskDraft,
    build_parse_prompt,
    parse_draft,
    parse_task,
)

TODAY = date(2026, 11, 2)


def draft_json(**overrides) -> str:
    """스키마를 만족하는 기본 JSON. 필요한 필드만 덮어쓴다."""
    data = {
        "title": "치과 예약",
        "due": "2026-11-03",
        "tags": ["건강"],
        "confidence": 0.95,
        "needs_clarification": None,
    }
    data.update(overrides)
    return json.dumps(data, ensure_ascii=False)


def test_schema_forbids_additional_properties_and_requires_all_fields():
    """스키마에 additionalProperties=False 가 있고 다섯 필드가 모두 required 다. 도구 정의도 같은 스키마를 쓴다."""
    pytest.fail("아직 구현하지 않음")


def test_prompt_puts_today_and_text_in_user_message():
    """user 에 '오늘: 2026-11-02' 와 <text>…</text> 로 감싼 입력이 있고, system 에는 날짜가 없다."""
    pytest.fail("아직 구현하지 않음")


def test_parse_draft_converts_due_string_to_date():
    """정상 JSON 은 TaskDraft 가 되고 due 는 date(2026, 11, 3) 이다."""
    pytest.fail("아직 구현하지 않음")


def test_parse_draft_rejects_invalid_json_and_unknown_fields():
    """JSON 이 아니거나 모르는 필드(note)가 있으면 DraftValidationError(code='schema')."""
    pytest.fail("아직 구현하지 않음")


def test_parse_draft_rejects_bad_date_format():
    """due='내일' 처럼 YYYY-MM-DD 가 아니면 code='bad_date'. 날짜 계산은 모델이, 검증은 내 코드가 한다."""
    pytest.fail("아직 구현하지 않음")


def test_parse_draft_rejects_empty_title_and_past_due():
    """공백 제목은 code='empty_title', 오늘보다 과거의 due 는 code='past_due' (서비스 계층 규칙과 동일)."""
    pytest.fail("아직 구현하지 않음")


def test_parse_draft_normalizes_tags():
    """tags 는 strip·소문자·중복 제거되며 순서는 유지된다: [' 건강', 'Health', '건강'] → ['건강', 'health']."""
    pytest.fail("아직 구현하지 않음")


def test_parse_task_returns_draft_for_confident_answer():
    """확신 높은 답은 TaskDraft 를 돌려주고, FakeLLM.calls 에 스키마가 전달돼 있다."""
    pytest.fail("아직 구현하지 않음")


def test_parse_task_raises_clarification_when_low_confidence_or_question():
    """confidence 0.5 또는 needs_clarification 이 있으면 ClarificationNeeded 이고 question 이 비어 있지 않다."""
    pytest.fail("아직 구현하지 않음")
