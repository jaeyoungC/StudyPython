"""44단원 테스트 뼈대. 실행: pytest units/44-llm-api-and-prompting

모든 테스트는 FakeLLM 만 씁니다. 네트워크·실제 API 키는 쓰지 않습니다.
`pytest.fail("아직 구현하지 않음")` 을 실제 검증으로 바꾸세요.
"""

from datetime import date

import pytest

from llm_client import (  # noqa: F401
    NO_OPEN_TASKS_MESSAGE,
    FakeLLM,
    LLMResult,
    TaskView,
    build_summary_prompt,
    get_llm,
    load_system_prompt,
    summarize_open_tasks,
)

TODAY = date(2026, 11, 2)


@pytest.fixture
def tasks():
    """마감 있는 것 둘(임박 순서는 뒤집어 둠), 마감 없는 것 하나, 완료된 것 하나."""
    return [
        TaskView(1, "세금 신고", False, date(2026, 11, 5)),
        TaskView(2, "운동화 사기", False, None),
        TaskView(3, "치과 예약", False, date(2026, 11, 3)),
        TaskView(4, "책 반납", True, date(2026, 11, 1)),
    ]


def test_fake_llm_returns_responses_in_order_and_records_calls():
    """FakeLLM 은 준비한 답을 순서대로 돌려주고, 받은 (system, user) 를 calls 에 기록한다."""
    pytest.fail("아직 구현하지 않음")


def test_fake_llm_raises_when_responses_exhausted():
    """준비한 답을 다 쓰면 RuntimeError — 테스트가 예상보다 많이 호출했다는 신호다."""
    pytest.fail("아직 구현하지 않음")


def test_system_prompt_file_loads_without_html_comments():
    """prompts/summary_system.md 를 읽으면 비어 있지 않고 '<!--' 주석이 제거돼 있다."""
    pytest.fail("아직 구현하지 않음")


def test_prompt_includes_only_open_tasks_sorted_by_due(tasks):
    """user 프롬프트에는 미완료만 들어가고, 마감 임박(치과 예약)이 세금 신고보다 앞, 마감 없음이 맨 뒤다."""
    pytest.fail("아직 구현하지 않음")


def test_prompt_puts_date_in_user_not_system(tasks):
    """오늘 날짜는 user 에만 있고 system 에는 없다 (system 은 캐시되는 고정 접두사)."""
    pytest.fail("아직 구현하지 않음")


def test_summary_skips_llm_when_no_open_tasks():
    """미완료가 없으면 LLM 을 호출하지 않고(calls 비어 있음) 고정 문구를 돌려준다."""
    pytest.fail("아직 구현하지 않음")


def test_summary_truncates_to_max_lines(tasks):
    """모델이 다섯 줄을 내도 결과는 max_lines=3 줄이다. 빈 줄은 세지 않는다."""
    pytest.fail("아직 구현하지 않음")


def test_get_llm_returns_none_without_api_key(monkeypatch):
    """ANTHROPIC_API_KEY 가 없으면 get_llm() 은 None — 기능을 정상적으로 끄는 길을 연다."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    pytest.fail("아직 구현하지 않음")
