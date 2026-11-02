"""44단원: LLM 을 외부 의존성 하나로 다룬다.

- `LLM` Protocol 뒤에 실제 클라이언트(`ClaudeLLM`)와 가짜(`FakeLLM`)를 둡니다.
- 테스트는 `FakeLLM` 만 씁니다. 네트워크 호출은 없습니다.
- 실제 호출은 환경 변수 ANTHROPIC_API_KEY 가 있을 때만 (`get_llm()`).

실제 프로젝트에서는 `todo/llm.py` 로 옮기세요.
설치(실제 호출에만 필요): `pip install anthropic python-dotenv`
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Protocol

# 모델 id 는 여기 한 곳에만. 날짜 접미사를 붙이지 않는다.
DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_MAX_TOKENS = 1024  # 세 줄 요약에는 충분. 긴 출력 기능이면 올리고 스트리밍을 고려
SYSTEM_PROMPT_PATH = Path(__file__).with_name("prompts") / "summary_system.md"
NO_OPEN_TASKS_MESSAGE = "미완료 할 일이 없습니다."


class LLMError(Exception):
    """LLM 호출 관련 오류의 부모."""


class LLMRefusedError(LLMError):
    """모델이 안전상의 이유로 응답을 거절함 (stop_reason == "refusal")."""


class LLMTruncatedError(LLMError):
    """max_tokens 에 걸려 응답이 잘림 (stop_reason == "max_tokens")."""


@dataclass(frozen=True)
class LLMResult:
    text: str
    input_tokens: int
    output_tokens: int
    stop_reason: str
    model: str


class LLM(Protocol):
    def complete(self, system: str, user: str) -> LLMResult: ...


# ---------------------------------------------------------------------------
# 가짜: 테스트용
# ---------------------------------------------------------------------------


class FakeLLM:
    """미리 정한 답을 순서대로 돌려주는 가짜.

    - responses: 돌려줄 문자열 목록. 다 쓰면 RuntimeError("준비된 응답이 없습니다")
    - calls: 받은 (system, user) 쌍을 순서대로 기록 → "프롬프트가 제대로 조립됐는가" 검사용
    - 토큰 수는 대략 글자 수 // 2 로 흉내 낸다 (실제 토큰화가 아님, 비용 추정 연습용)
    """

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, user: str) -> LLMResult:
        # TODO
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 실제 클라이언트
# ---------------------------------------------------------------------------


class ClaudeLLM:
    """Anthropic SDK 로 Messages API 를 호출한다.

    - model: 기본 DEFAULT_MODEL
    - effort: "low" | "medium" | "high". 짧은 요약은 "low" 로 충분하다
    - enable_fallbacks: True 면 안전 거절 시 서버가 다른 모델로 다시 시도한다
      (client.beta.messages.create + betas=["server-side-fallback-2026-07-01"] + fallbacks="default")
      False 면 client.messages.create 를 쓴다

    구현 요령:
      1. anthropic 은 이 클래스 안에서 import (설치 없이도 FakeLLM 테스트가 돌게)
      2. 응답의 stop_reason 을 먼저 본다: "refusal" → LLMRefusedError, "max_tokens" → LLMTruncatedError
      3. content 는 블록 리스트. block.type == "text" 인 것만 이어 붙인다
      4. usage.input_tokens / usage.output_tokens 를 LLMResult 에 담는다
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        effort: str = "low",
        max_tokens: int = DEFAULT_MAX_TOKENS,
        enable_fallbacks: bool = True,
    ) -> None:
        import anthropic  # 지연 import

        self._client = anthropic.Anthropic()  # ANTHROPIC_API_KEY 를 환경에서 읽는다
        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens
        self.enable_fallbacks = enable_fallbacks

    def complete(self, system: str, user: str) -> LLMResult:
        # TODO
        # 힌트 (fallbacks 켠 경우):
        # response = self._client.beta.messages.create(
        #     model=self.model, max_tokens=self.max_tokens,
        #     system=system, messages=[{"role": "user", "content": user}],
        #     output_config={"effort": self.effort},
        #     betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        # )
        raise NotImplementedError


def get_llm() -> LLM | None:
    """ANTHROPIC_API_KEY 가 있으면 ClaudeLLM, 없으면 None.

    None 이면 기능을 '정상적으로 끄는' 것이 호출자의 책임이다 (28단원 점진적 기능 저하).
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 첫 기능: 오늘의 미완료 할 일 요약
# ---------------------------------------------------------------------------


@dataclass
class TaskView:
    """요약에 필요한 최소 필드. 실제 프로젝트에서는 Task 에서 변환한다."""

    id: int
    title: str
    done: bool
    due: date | None = None


def load_system_prompt(path: Path = SYSTEM_PROMPT_PATH) -> str:
    """prompts/summary_system.md 를 읽어 돌려준다. HTML 주석(<!-- -->)은 제거한다."""
    # TODO
    raise NotImplementedError


def build_summary_prompt(tasks: list[TaskView], today: date) -> tuple[str, str]:
    """(system, user) 를 돌려준다.

    - system: load_system_prompt()
    - user: 오늘 날짜 한 줄 + <tasks> 태그 안에 미완료 할 일만, 한 줄에 하나:
        "- [id=3] 세금 신고 (마감 2026-11-05, D-3)"  /  마감 없음이면 "(마감 없음)"
      정렬: 마감 있는 것을 임박한 순으로 먼저, 마감 없는 것은 id 순으로 뒤에
    - 날짜는 user 쪽에만 넣는다 (system 은 캐시되는 고정 접두사)
    """
    # TODO
    raise NotImplementedError


def summarize_open_tasks(
    llm: LLM,
    tasks: list[TaskView],
    today: date,
    max_lines: int = 3,
) -> str:
    """미완료 할 일을 최대 max_lines 줄로 요약한다.

    - 미완료가 없으면 LLM 을 부르지 않고 NO_OPEN_TASKS_MESSAGE
    - 모델이 더 많은 줄을 내면 앞 max_lines 줄만 (빈 줄은 센 뒤 제거하지 말고 먼저 제거)
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    # 과제 B: 실제 호출. `.env` 에 ANTHROPIC_API_KEY 를 두고 `python llm_client.py`
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    llm = get_llm()
    if llm is None:
        raise SystemExit("ANTHROPIC_API_KEY 가 없습니다. .env 를 확인하세요.")
    sample = [
        TaskView(1, "세금 신고", False, date(2026, 11, 5)),
        TaskView(2, "운동화 사기", False, None),
        TaskView(3, "치과 예약", False, date(2026, 11, 3)),
        TaskView(4, "책 반납", True, date(2026, 11, 1)),
    ]
    print(summarize_open_tasks(llm, sample, today=date(2026, 11, 2)))
