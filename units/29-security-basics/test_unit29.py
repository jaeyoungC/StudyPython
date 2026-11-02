"""29단원 테스트 뼈대. 실행: pytest units/29-security-basics

각 테스트는 vulnerable_app.py 의 문제 하나가 '고쳐졌음'을 증명합니다. 본문을 채우세요.
고치기 전에 먼저 이 테스트들이 실패하는 것(취약함)을 확인하면 더 좋습니다.
"""

import sqlite3

import pytest

import vulnerable_app as app


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    app.init_schema(c)
    yield c
    c.close()


# ---------------------------------------------------------------------------
# 문제 2: SQL 인젝션
# ---------------------------------------------------------------------------


def test_title_search_with_quote_returns_only_exact_match(conn):
    """제목 "a' OR '1'='1" 로 검색하면 모든 행이 아니라 정확히 그 제목인 행(없으면 빈 리스트)만 돌아온다."""
    pytest.fail("아직 구현하지 않음")


def test_login_with_injected_username_fails(conn):
    """username "' OR '1'='1' --" 로 로그인하면 False 또는 ValueError 이어야 하고, 절대 True 가 아니다."""
    pytest.fail("아직 구현하지 않음")


# ---------------------------------------------------------------------------
# 문제 3: 입력 검증
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_title", [None, "", "   ", 123, "x" * 10_001])
def test_create_task_rejects_invalid_titles(conn, bad_title):
    """None·빈 문자열·공백·문자열 아님·너무 긴 제목은 ValueError. DB 에 아무 행도 생기지 않는다."""
    pytest.fail("아직 구현하지 않음")


def test_create_task_strips_and_stores_valid_title(conn):
    """"  산책  " 은 "산책" 으로 저장된다 (03단원 규칙과 같다)."""
    pytest.fail("아직 구현하지 않음")


# ---------------------------------------------------------------------------
# 문제 4: 비밀번호 저장
# ---------------------------------------------------------------------------


def test_password_is_not_stored_in_plain_text(conn):
    """register 뒤 users 테이블의 password 열에 원문이 들어 있지 않다."""
    pytest.fail("아직 구현하지 않음")


def test_login_succeeds_with_correct_password_and_fails_otherwise(conn):
    """맞는 비밀번호는 True, 틀린 비밀번호는 False. 해시를 비교할 때 hmac.compare_digest 또는 라이브러리의 verify 를 쓴다."""
    pytest.fail("아직 구현하지 않음")


def test_login_does_not_reveal_whether_user_exists(conn):
    """없는 사용자와 틀린 비밀번호가 같은 방식(둘 다 False)으로 응답한다."""
    pytest.fail("아직 구현하지 않음")


# ---------------------------------------------------------------------------
# 문제 1: 비밀값
# ---------------------------------------------------------------------------


def test_secret_is_read_from_environment(monkeypatch):
    """API_SECRET 은 환경 변수 TODO_API_SECRET 에서 읽는 함수(get_api_secret)로 바뀌고, 없으면 RuntimeError.
    monkeypatch.setenv / delenv 를 쓴다. 소스 파일 안에 'sk-live' 문자열이 남아 있지 않은지도 확인한다."""
    pytest.fail("아직 구현하지 않음")


# ---------------------------------------------------------------------------
# 문제 5: 난수
# ---------------------------------------------------------------------------


def test_reset_token_uses_secrets_and_is_long_enough():
    """make_reset_token 은 secrets.token_urlsafe(32) 같은 값을 돌려준다: 100번 만들어 모두 다르고 길이가 32 이상이다.
    inspect.getsource 로 'random.' 이 더 이상 쓰이지 않는지 확인해도 된다."""
    pytest.fail("아직 구현하지 않음")


# ---------------------------------------------------------------------------
# 문제 6: 경로 탐색
# ---------------------------------------------------------------------------


def test_read_export_rejects_paths_outside_export_dir(tmp_path, monkeypatch):
    """EXPORT_DIR 을 tmp_path/exports 로 바꾼 뒤, "../secret.txt" 를 읽으려 하면 ValueError. (Path.resolve 와 is_relative_to)"""
    pytest.fail("아직 구현하지 않음")


def test_read_export_reads_file_inside_export_dir(tmp_path, monkeypatch):
    """exports/report.txt 는 정상적으로 읽힌다."""
    pytest.fail("아직 구현하지 않음")
