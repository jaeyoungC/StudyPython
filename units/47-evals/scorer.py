"""47단원: 평가 세트 로더와 채점기. 네트워크 없음 — 출력은 밖에서 받아 넣는다.

실제 프로젝트에서는 `evals/scorer.py` 로 옮기고, 실행 스크립트(`evals/run.py`)가
세트를 읽어 parse_task 를 돌린 뒤 여기 함수로 채점하게 하세요.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

WEIGHTS = {"title": 0.4, "due": 0.3, "tags": 0.2, "clarification": 0.1}
FAIL_THRESHOLD = 0.5


@dataclass
class EvalCase:
    id: str
    input: str
    today: str
    expected: dict[str, Any]  # title, due, tags, needs_clarification(bool)
    tags: list[str] = field(default_factory=list)


@dataclass
class CaseScore:
    case_id: str
    title: float
    due: float
    tags: float
    clarification: float
    total: float
    case_tags: list[str] = field(default_factory=list)


@dataclass
class Report:
    mean_total: float
    by_field: dict[str, float]
    by_tag: dict[str, float]
    failures: list[str]
    n: int


# ---------------------------------------------------------------------------
# 세트 읽기
# ---------------------------------------------------------------------------


def load_eval_set(path: Path) -> list[EvalCase]:
    """JSONL 한 줄 = 사례 하나. 빈 줄은 건너뛰고, 깨진 줄은 ValueError(f"{줄 번호}번째 줄: ...").

    필수 키: id, input, today, expected. tags 는 없으면 [].
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 필드별 채점
# ---------------------------------------------------------------------------


def normalize_title(s: str | None) -> str:
    """None → "". 앞뒤·연속 공백 정리, 끝의 "하기" 제거, 소문자.
    예: "  치과 예약하기 " → "치과 예약"
    """
    # TODO
    raise NotImplementedError


def score_title(expected: str | None, actual: str | None) -> float:
    """정규화 후 같으면 1.0. 아니면 공백으로 나눈 토큰 집합의 자카드 유사도(교집합/합집합).
    둘 다 비면 1.0, 하나만 비면 0.0.
    """
    # TODO
    raise NotImplementedError


def score_due(expected: str | None, actual: str | None) -> float:
    """정확 일치만 1.0 (None == None 도 일치). 날짜는 비슷해도 틀린 것이다."""
    # TODO
    raise NotImplementedError


def score_tags(expected: list[str], actual: list[str]) -> float:
    """집합 F1. 둘 다 비면 1.0, 하나만 비면 0.0. 비교 전 소문자·strip."""
    # TODO
    raise NotImplementedError


def score_clarification(expected_needs: bool, actual_question: str | None) -> float:
    """기대가 '질문해야 함' 이면 질문이 있어야 1.0, '질문 불필요' 면 질문이 없어야 1.0."""
    # TODO
    raise NotImplementedError


def score_case(case: EvalCase, output: dict[str, Any]) -> CaseScore:
    """output 은 parse_task 결과를 dict 로 바꾼 것: title, due(str|None), tags, needs_clarification(str|None).
    total = 가중 평균(WEIGHTS)."""
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 집계와 회귀 관문
# ---------------------------------------------------------------------------


def aggregate(scores: list[CaseScore]) -> Report:
    """평균 total, 필드별 평균, 사례 태그별 평균(태그가 여러 개면 각각에 포함), total < FAIL_THRESHOLD 인 case_id.
    scores 가 비면 ValueError."""
    # TODO
    raise NotImplementedError


def regression_check(report: Report, baseline_total: float, tolerance: float = 0.02) -> bool:
    """report.mean_total >= baseline_total - tolerance 이면 True(통과)."""
    # TODO
    raise NotImplementedError


def expected_as_output(case: EvalCase) -> dict[str, Any]:
    """오라클 검사용: 기대값을 그대로 출력 형태로 바꾼다 (needs_clarification True → 질문 문자열)."""
    exp = case.expected
    return {
        "title": exp.get("title"),
        "due": exp.get("due"),
        "tags": list(exp.get("tags", [])),
        "needs_clarification": "확인이 필요합니다" if exp.get("needs_clarification") else None,
    }


NULL_OUTPUT: dict[str, Any] = {"title": "", "due": None, "tags": [], "needs_clarification": None}
