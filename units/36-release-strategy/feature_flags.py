"""36단원: 기능 플래그(feature flag) 뼈대.

배포(deploy)와 릴리스(release)를 분리하는 가장 작은 도구입니다. 코드는 이미 운영에 나가 있지만 플래그가 꺼져 있으면 아무도 못 봅니다.
플래그를 켜는 것이 릴리스이고, 끄는 것이 가장 빠른 롤백입니다.

이 단원은 ○ 이므로 테스트 파일이 없습니다. 직접 test_unit36.py 를 만들어 아래 docstring 의 규칙을 테스트로 옮기세요(최소 6개).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class Flag:
    """플래그 하나.

    name:        예: "notifications_v2"
    enabled:     전체 스위치. False 면 아래 조건과 무관하게 꺼짐
    percentage:  0~100. 사용자 id 를 해시해 이 비율만큼만 켠다(카나리). 같은 사용자는 항상 같은 결과여야 한다
    allow_users: 비율과 무관하게 항상 켜는 사용자(내부 테스터)
    """

    name: str
    enabled: bool = False
    percentage: int = 100
    allow_users: frozenset[str] = field(default_factory=frozenset)


class FeatureFlags:
    """플래그 묶음. 운영에서는 환경 변수나 파일에서 읽고(35단원 Settings), 바뀌면 재시작 없이 다시 읽는 것이 목표."""

    def __init__(self, flags: Mapping[str, Flag]) -> None:
        self._flags = dict(flags)

    def is_enabled(self, name: str, *, user_id: str | None = None) -> bool:
        """규칙:
        - 모르는 플래그 이름은 False (안전한 기본값 — 켜진 적 없는 기능은 꺼져 있다)
        - enabled=False 면 False
        - user_id 가 allow_users 에 있으면 True
        - percentage 가 100 이면 True
        - user_id 가 None 이면 False (비율 판단 불가)
        - bucket(name, user_id) < percentage 면 True
        """
        # TODO
        raise NotImplementedError

    @staticmethod
    def bucket(name: str, user_id: str) -> int:
        """0~99. sha256(f"{name}:{user_id}") 의 첫 4바이트를 정수로 읽어 % 100.
        플래그 이름을 섞는 이유: 모든 플래그가 같은 10% 사용자에게만 몰리지 않게 하려고.
        """
        # TODO
        raise NotImplementedError

    @classmethod
    def from_env(cls, env: Mapping[str, str], prefix: str = "FLAG_") -> "FeatureFlags":
        """FLAG_NOTIFICATIONS_V2="on" / "off" / "25%" / "on:alice,bob" 같은 형식을 읽는다. 형식은 직접 정하고 docstring 에 적는다."""
        # TODO
        raise NotImplementedError
