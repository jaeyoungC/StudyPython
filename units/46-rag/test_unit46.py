"""46단원 테스트 뼈대. 실행: pytest units/46-rag

청킹과 검색(SQLite :memory:)만 검사합니다. LLM 은 FakeLLM 으로 프롬프트 조립만 봅니다.
`pytest.fail("아직 구현하지 않음")` 을 실제 검증으로 바꾸세요.
"""

import sqlite3

import pytest

from rag import (  # noqa: F401
    NO_EVIDENCE_MESSAGE,
    FakeLLM,
    Fts5Index,
    Hit,
    answer,
    assemble_context,
    build_ask_prompt,
    chunk_text,
    sanitize_query,
)


@pytest.fixture
def index():
    """:memory: FTS5 인덱스에 할 일 네 건을 넣어 둔다 (제목 + 메모)."""
    conn = sqlite3.connect(":memory:")
    idx = Fts5Index(conn, size=200, overlap=40)
    try:
        idx.init_schema()
        idx.add(1, "치과 예약. 스케일링 받고 사랑니 상담하기. 태그: 건강")
        idx.add(2, "세금 신고. 홈택스에서 종합소득세 신고. 태그: 돈")
        idx.add(3, "운동화 사기. 러닝용으로 가벼운 것. 태그: 쇼핑 건강")
        idx.add(4, "책 반납. 도서관에 소설 두 권. 태그: 집안일")
    except NotImplementedError:
        # Fts5Index 를 구현하기 전에는 None 을 넘긴다. 테스트 본문이 먼저 실패 메시지를 낸다.
        return None
    return idx


def test_chunk_short_text_is_single_chunk():
    """size 이하의 텍스트는 조각 하나, 빈 문자열과 공백뿐인 문자열은 []."""
    pytest.fail("아직 구현하지 않음")


def test_chunk_overlap_repeats_tail_of_previous_chunk():
    """chunk_text('abcdefghij', size=4, overlap=1) == ['abcd', 'defg', 'ghij'] — 겹침이 앞 조각의 끝을 포함한다."""
    pytest.fail("아직 구현하지 않음")


def test_chunk_rejects_overlap_not_smaller_than_size():
    """overlap >= size 또는 size <= 0 이면 ValueError (무한 루프를 막는다)."""
    pytest.fail("아직 구현하지 않음")


def test_sanitize_query_quotes_terms_and_strips_fts_syntax():
    """'치과 \"예약\"' 은 '\"치과\" \"예약\"' 이 되고, FTS 문법 문자만 있는 질의는 '' 이 된다."""
    pytest.fail("아직 구현하지 않음")


def test_search_returns_matching_task_first(index):
    """'치과' 검색의 첫 결과는 task_id=1 이고 score 가 숫자다."""
    pytest.fail("아직 구현하지 않음")


def test_search_respects_k_and_returns_empty_for_no_match(index):
    """'건강' 은 두 건(1, 3)이 걸리지만 k=1 이면 하나만, '우주선' 은 [] 다."""
    pytest.fail("아직 구현하지 않음")


def test_remove_drops_chunks_of_task(index):
    """remove(1) 뒤에는 '치과' 검색이 비고, 다른 할 일은 그대로 검색된다 (재색인의 기초)."""
    pytest.fail("아직 구현하지 않음")


def test_assemble_context_stops_at_budget_without_cutting():
    """예산 안에 들어가는 조각만 점수 순으로 넣고, 넘치는 첫 조각에서 멈추며 조각을 자르지 않는다."""
    pytest.fail("아직 구현하지 않음")


def test_answer_skips_llm_when_no_hits(index):
    """검색 0건이면 FakeLLM.calls 가 비어 있고 NO_EVIDENCE_MESSAGE 를 돌려준다."""
    pytest.fail("아직 구현하지 않음")


def test_answer_puts_context_and_question_in_user_prompt(index):
    """히트가 있으면 user 프롬프트에 <context> 안의 '[task_id=1]' 과 <question> 안의 질문이 들어 있다."""
    pytest.fail("아직 구현하지 않음")
