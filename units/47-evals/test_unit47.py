"""47단원 테스트 뼈대. 실행: pytest units/47-evals

채점기만 검사합니다. 모델 호출 없음. `pytest.fail("아직 구현하지 않음")` 을 실제 검증으로 바꾸세요.
"""

from pathlib import Path

import pytest

from scorer import (  # noqa: F401
    FAIL_THRESHOLD,
    NULL_OUTPUT,
    WEIGHTS,
    CaseScore,
    EvalCase,
    aggregate,
    expected_as_output,
    load_eval_set,
    normalize_title,
    regression_check,
    score_case,
    score_clarification,
    score_due,
    score_tags,
    score_title,
)

EVAL_SET = Path(__file__).with_name("evals") / "parse_eval_set.jsonl"


@pytest.fixture
def cases():
    try:
        return load_eval_set(EVAL_SET)
    except NotImplementedError:
        # load_eval_set 을 구현하기 전에는 None 을 넘긴다. 테스트 본문이 먼저 실패 메시지를 낸다.
        return None


def test_load_eval_set_reads_all_cases_with_tags(cases):
    """제공된 세트는 10개 이상이고, 모든 사례에 id·input·today·expected 가 있으며 tags 는 리스트다."""
    pytest.fail("아직 구현하지 않음")


def test_load_eval_set_reports_line_number_for_broken_line(tmp_path):
    """깨진 JSON 줄이 있으면 ValueError 메시지에 그 줄 번호가 들어 있다."""
    pytest.fail("아직 구현하지 않음")


def test_normalize_title_strips_spaces_and_trailing_hagi():
    """'  치과 예약하기 ' → '치과 예약', None → ''."""
    pytest.fail("아직 구현하지 않음")


def test_score_title_exact_after_normalization_and_partial_overlap():
    """'치과 예약하기' vs '치과 예약' 은 1.0, '러닝용 운동화 사기' vs '운동화 사기' 는 0 과 1 사이."""
    pytest.fail("아직 구현하지 않음")


def test_score_due_is_exact_match_only():
    """같은 날짜 1.0, 하루 차이 0.0, None 과 None 은 1.0, None 과 날짜는 0.0."""
    pytest.fail("아직 구현하지 않음")


def test_score_tags_is_set_f1():
    """['쇼핑','건강'] vs ['건강'] 은 F1 = 2/3 에 가깝고, 둘 다 빈 리스트면 1.0."""
    pytest.fail("아직 구현하지 않음")


def test_score_case_weights_sum_to_one_and_total_is_weighted_mean():
    """WEIGHTS 합은 1.0 이고, 필드 점수가 (1, 0, 1, 1) 이면 total 은 0.7 이다."""
    pytest.fail("아직 구현하지 않음")


def test_oracle_scores_one_and_null_scores_low(cases):
    """기대값을 출력으로 넣으면 모든 사례 total == 1.0 (오라클), NULL_OUTPUT 은 평균 total < 0.3 (널). 둘 중 하나라도 어긋나면 채점기가 고장난 것."""
    pytest.fail("아직 구현하지 않음")


def test_aggregate_reports_by_field_by_tag_and_failures():
    """두 사례(하나는 total 0.2)를 집계하면 failures 에 그 id 가 있고 by_tag 에 사례 태그별 평균이 있다."""
    pytest.fail("아직 구현하지 않음")


def test_regression_check_allows_small_drop_only():
    """기준선 0.80: 평균 0.79 는 통과, 0.77 은 실패 (tolerance 0.02)."""
    pytest.fail("아직 구현하지 않음")
