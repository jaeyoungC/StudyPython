"""14단원: 개인정보(PII, personally identifiable information) 분류와 가림(redaction).

할 일 제목에는 무엇이든 들어온다 — "김민수 010-1234-5678 에게 전화", "a@b.com 에 답장". 로그·검색 색인·에이전트 프롬프트에
그대로 흘러가면 그 자리가 전부 개인정보 저장소가 된다. 이 모듈은 (1) 필드마다 등급을 선언하고 (2) 자유 텍스트에서 흔한 패턴을 가린다.
"""

from __future__ import annotations

import re
from enum import Enum


class Sensitivity(Enum):
    PUBLIC = "public"  # 누구나 봐도 되는 값 (id, done)
    INTERNAL = "internal"  # 서비스 안에서만 (title, tags, due)
    PERSONAL = "personal"  # 특정인을 식별할 수 있는 값 (actor, 제목 속 이름·연락처)
    SECRET = "secret"  # 비밀번호, 토큰 — 저장도 로그도 금지


# README 의 PII 분류표를 코드로 옮긴 것. 새 필드를 추가할 때 여기에도 한 줄을 더하는 것이 규칙이다.
FIELD_SENSITIVITY: dict[str, Sensitivity] = {
    # TODO: tasks·audit_log 의 모든 열을 적는다. 예: "tasks.id": Sensitivity.PUBLIC, "tasks.title": Sensitivity.INTERNAL, ...
}

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE_KR = re.compile(r"01[016789]-?\d{3,4}-?\d{4}")


def classify(field: str) -> Sensitivity:
    """"tasks.title" 같은 필드 이름의 등급. 표에 없는 필드는 **가장 엄격한** SECRET 로 본다 (모르는 것은 민감하다고 가정)."""
    # TODO
    raise NotImplementedError


def redact(text: str) -> str:
    """이메일과 한국 휴대전화 번호를 "[email]", "[phone]" 으로 바꾼 새 문자열. 로그와 에이전트 프롬프트에 넣기 전에 통과시킨다."""
    # TODO
    raise NotImplementedError
