"""35단원: 설정을 코드에서 분리한다 — 환경 변수에서 읽는 Settings.

12-factor 의 "설정(config)" 원칙: 배포 환경마다 달라지는 값(DB 경로, 포트, 비밀값, 로그 레벨)은 코드가 아니라 환경에 둔다.
같은 이미지가 개발·테스트·운영에서 환경 변수만 바꿔 돈다.

뼈대만 있습니다. test_unit35.py 의 뼈대를 먼저 채운 뒤 구현하세요.
프로젝트에서는 todo/config.py 로 옮깁니다(이 저장소에서는 다른 단원과 모듈 이름이 겹치지 않도록 app_config 라는 이름을 씁니다).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Mapping


class ConfigError(ValueError):
    """설정이 빠졌거나 잘못됐다. 앱은 시작하지 않아야 한다(절반만 설정된 채로 뜨는 것보다 낫다)."""


@dataclass(frozen=True)
class Settings:
    """앱이 쓰는 모든 설정. frozen 이라 실행 중에 바뀌지 않는다."""

    api_secret: str  # 필수. 기본값 없음 — 없으면 ConfigError
    database_path: str = "todo.db"  # TODO_DATABASE_PATH
    host: str = "127.0.0.1"  # TODO_HOST
    port: int = 8000  # TODO_PORT, 1~65535
    log_level: int = logging.INFO  # TODO_LOG_LEVEL: "DEBUG" | "INFO" | "WARNING" | "ERROR"
    notifier_url: str | None = None  # TODO_NOTIFIER_URL. 없으면 알림 기능 비활성(28단원: 부가 기능)
    rate_limit_rate: float = 5.0  # TODO_RATE_LIMIT_RATE (27단원)
    rate_limit_capacity: int = 20  # TODO_RATE_LIMIT_CAPACITY
    environment: str = "development"  # TODO_ENV: development | test | production


PREFIX = "TODO_"


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """환경 변수(기본은 os.environ)에서 Settings 를 만든다.

    - env 를 인자로 받는 이유: 테스트에서 dict 를 넣기 위해 (os.environ 을 직접 읽으면 테스트가 서로 간섭한다)
    - TODO_API_SECRET 이 없거나 빈 문자열이면 ConfigError("TODO_API_SECRET ...")
    - TODO_PORT 가 정수가 아니거나 1~65535 밖이면 ConfigError
    - TODO_LOG_LEVEL 은 대소문자 무시, 모르는 이름이면 ConfigError
    - TODO_ENV 가 "production" 인데 api_secret 이 "changeme" 같은 알려진 기본값이면 ConfigError (운영에서 기본 비밀값 금지)
    - 그 밖의 값은 없으면 Settings 의 기본값
    힌트: int(), float() 의 ValueError 를 잡아 ConfigError 로 바꾼다(07단원의 raise from)
    """
    # TODO
    raise NotImplementedError


def health_payload(settings: Settings, *, database_ok: bool, dependencies: Mapping[str, str] | None = None) -> dict:
    """GET /health 응답 본문.

    {"status": "ok" | "degraded" | "down", "environment": ..., "checks": {"database": "ok"|"fail", ...}}
    - database_ok 가 False 면 "down" (핵심 기능 불가)
    - dependencies(예: {"notifier": "open"}) 중 "ok" 가 아닌 것이 있으면 "degraded" (28단원)
    - 비밀값·DB 경로 같은 설정 값은 절대 넣지 않는다(29단원)
    """
    # TODO
    raise NotImplementedError
