"""35단원 테스트 뼈대. 실행: pytest units/35-deployment

load_settings 는 dict 를 받으므로 os.environ 을 건드리지 않고 테스트합니다. 본문을 채우세요.
"""

import logging

import pytest

from app_config import ConfigError, Settings, health_payload, load_settings

BASE = {"TODO_API_SECRET": "test-secret"}


def test_defaults_apply_when_only_secret_is_set():
    """BASE 만 주면 port 8000, host 127.0.0.1, database_path "todo.db", log_level INFO, notifier_url None."""
    pytest.fail("아직 구현하지 않음")


def test_missing_secret_is_a_config_error():
    """{} 또는 {"TODO_API_SECRET": ""} 는 ConfigError 이고 메시지에 변수 이름이 들어 있다."""
    pytest.fail("아직 구현하지 않음")


def test_environment_overrides_defaults():
    """TODO_PORT=9000, TODO_HOST=0.0.0.0, TODO_DATABASE_PATH=/data/todo.db 가 반영된다."""
    pytest.fail("아직 구현하지 않음")


@pytest.mark.parametrize("port", ["abc", "0", "70000", "-1", "80.5"])
def test_invalid_port_is_a_config_error(port):
    """정수가 아니거나 범위 밖이면 ConfigError."""
    pytest.fail("아직 구현하지 않음")


@pytest.mark.parametrize("name, level", [("debug", logging.DEBUG), ("INFO", logging.INFO), ("Warning", logging.WARNING)])
def test_log_level_names_are_case_insensitive(name, level):
    """TODO_LOG_LEVEL 이름 → logging 상수."""
    pytest.fail("아직 구현하지 않음")


def test_unknown_log_level_is_a_config_error():
    """TODO_LOG_LEVEL=VERBOSE 는 ConfigError."""
    pytest.fail("아직 구현하지 않음")


def test_production_rejects_default_secret():
    """TODO_ENV=production 과 TODO_API_SECRET=changeme 의 조합은 ConfigError. development 에서는 허용."""
    pytest.fail("아직 구현하지 않음")


def test_settings_are_immutable():
    """settings.port = 1 은 dataclasses.FrozenInstanceError."""
    pytest.fail("아직 구현하지 않음")


def test_health_ok_when_everything_is_fine():
    """database_ok=True, dependencies={"notifier": "ok"} → status "ok", checks.database "ok"."""
    pytest.fail("아직 구현하지 않음")


def test_health_degraded_when_dependency_is_not_ok():
    """dependencies={"notifier": "open"} → "degraded" (완료는 되지만 알림은 안 나감)."""
    pytest.fail("아직 구현하지 않음")


def test_health_down_when_database_fails():
    """database_ok=False → "down", 의존성 상태와 무관."""
    pytest.fail("아직 구현하지 않음")


def test_health_payload_never_leaks_secrets():
    """payload 를 json.dumps 한 문자열에 api_secret 과 database_path 가 들어 있지 않다."""
    pytest.fail("아직 구현하지 않음")
