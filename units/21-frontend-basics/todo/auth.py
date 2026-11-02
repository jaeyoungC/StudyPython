"""인증(authentication, 누구인가)과 토큰 (18단원). 표준 라이브러리만 쓴다.

- 비밀번호는 절대 그대로 저장하지 않는다. hashlib.scrypt 로 느리게 해싱하고, 사용자마다 다른 salt 를 섞는다.
- 토큰은 secrets 로 만들고, 저장소에는 토큰의 sha256 해시만 둔다. 저장소가 새어도 토큰은 못 쓴다.
- 비교는 hmac.compare_digest 로 한다. 일반 == 는 첫 글자가 다르면 빨리 끝나 시간 차이로 정보가 샌다(timing attack).

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
    salt = salt if salt is not None else secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, **SCRYPT_PARAMS)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """stored 의 salt 로 다시 해싱해 상수 시간 비교한다. 형식이 틀리면 False."""
    try:
        scheme, salt_hex, _ = stored.split("$")
    except ValueError:
        return False
    if scheme != "scrypt":
        return False
    recomputed = hash_password(password, salt=bytes.fromhex(salt_hex))
    return hmac.compare_digest(recomputed, stored)


def new_token() -> str:
    """URL 에 넣어도 안전한 무작위 토큰. 예측 불가능해야 하므로 random 이 아니라 secrets 를 쓴다."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """토큰은 길고 무작위라 salt 없이 sha256 한 번이면 충분하다(비밀번호와 다른 점)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class UserStore:
    """메모리 사용자·토큰 저장소. 서버를 재시작하면 모두 사라진다 (질문 4)."""

    def __init__(self, clock: Callable[[], datetime] = datetime.now, token_ttl: timedelta = timedelta(hours=12)) -> None:
        self.clock = clock
        self.token_ttl = token_ttl
        self._users: dict[str, User] = {}  # username → User
        self._tokens: dict[str, tuple[int, datetime]] = {}  # token hash → (user id, 만료 시각)

    def register(self, username: str, password: str) -> User:
        """규칙: 이름 중복 금지(ValueError), 비밀번호 8자 이상(ValueError)."""
        username = username.strip()
        if not username:
            raise ValueError("사용자 이름은 비어 있을 수 없습니다")
        if username in self._users:
            raise ValueError(f"이미 있는 사용자 이름입니다: {username}")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"비밀번호는 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다")
        user = User(id=len(self._users) + 1, username=username, password_hash=hash_password(password))
        self._users[username] = user
        return user

    def login(self, username: str, password: str) -> str:
        """맞으면 새 토큰 문자열, 틀리면 AuthError. 이름이 없든 비밀번호가 틀리든 같은 메시지."""
        user = self._users.get(username.strip())
        if user is None or not verify_password(password, user.password_hash):
            raise AuthError("사용자 이름 또는 비밀번호가 올바르지 않습니다")
        token = new_token()
        self._tokens[hash_token(token)] = (user.id, self.clock() + self.token_ttl)
        return token

    def user_for_token(self, token: str) -> User:
        """토큰이 없거나 만료됐으면 AuthError."""
        entry = self._tokens.get(hash_token(token))
        if entry is None:
            raise AuthError("토큰이 올바르지 않습니다")
        user_id, expires_at = entry
        if self.clock() >= expires_at:
            del self._tokens[hash_token(token)]
            raise AuthError("토큰이 만료되었습니다")
        return next(u for u in self._users.values() if u.id == user_id)

    def revoke(self, token: str) -> None:
        self._tokens.pop(hash_token(token), None)
