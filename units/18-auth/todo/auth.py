"""인증(authentication, 누구인가)과 토큰 (18단원). 표준 라이브러리만 쓴다.

- 비밀번호는 절대 그대로 저장하지 않는다. hashlib.scrypt 로 느리게 해싱하고, 사용자마다 다른 salt 를 섞는다.
- 토큰은 secrets 로 만들고, 저장소에는 토큰의 sha256 해시만 둔다. 저장소가 새어도 토큰은 못 쓴다.
- 비교는 hmac.compare_digest 로 한다. 일반 == 는 첫 글자가 다르면 빨리 끝나 시간 차이로 정보가 샌다(timing attack).

과제: 모든 TODO 를 채우세요. 힌트는 각 docstring 과 README 의 표에 있습니다.
인가(authorization, 무엇을 할 수 있는가)는 여기 없다. 소유권 검사는 TaskService 가 owner_id 로 한다.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

SCRYPT_PARAMS = {"n": 2**14, "r": 8, "p": 1}  # 2026년 기준 무난한 값. 더 크면 더 느리고 더 안전하다.
MIN_PASSWORD_LENGTH = 8


class AuthError(Exception):
    """자격 증명이 틀렸거나 토큰이 없거나 만료됐을 때 → HTTP 401."""


@dataclass
class User:
    id: int
    username: str
    password_hash: str


def hash_password(password: str, *, salt: bytes | None = None) -> str:
    """'scrypt$<salt hex>$<hash hex>' 문자열. salt 를 주지 않으면 새로 만든다."""
    # TODO
    raise NotImplementedError


def verify_password(password: str, stored: str) -> bool:
    """stored 의 salt 로 다시 해싱해 상수 시간 비교한다. 형식이 틀리면 False."""
    # TODO
    raise NotImplementedError


def new_token() -> str:
    """URL 에 넣어도 안전한 무작위 토큰. 예측 불가능해야 하므로 random 이 아니라 secrets 를 쓴다."""
    # TODO
    raise NotImplementedError


def hash_token(token: str) -> str:
    """토큰은 길고 무작위라 salt 없이 sha256 한 번이면 충분하다(비밀번호와 다른 점)."""
    # TODO
    raise NotImplementedError


class UserStore:
    """메모리 사용자·토큰 저장소. 서버를 재시작하면 모두 사라진다 (질문 4)."""

    def __init__(self, clock: Callable[[], datetime] = datetime.now, token_ttl: timedelta = timedelta(hours=12)) -> None:
        self.clock = clock
        self.token_ttl = token_ttl
        self._users: dict[str, User] = {}  # username → User
        self._tokens: dict[str, tuple[int, datetime]] = {}  # token hash → (user id, 만료 시각)

    def register(self, username: str, password: str) -> User:
        """규칙: 이름 중복 금지(ValueError), 비밀번호 8자 이상(ValueError)."""
        # TODO
        raise NotImplementedError

    def login(self, username: str, password: str) -> str:
        """맞으면 새 토큰 문자열, 틀리면 AuthError. 이름이 없든 비밀번호가 틀리든 같은 메시지."""
        # TODO
        raise NotImplementedError

    def user_for_token(self, token: str) -> User:
        """토큰이 없거나 만료됐으면 AuthError."""
        # TODO
        raise NotImplementedError

    def revoke(self, token: str) -> None:
        # TODO
        raise NotImplementedError
