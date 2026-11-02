"""18단원 테스트 뼈대. 실행: pytest units/18-auth

◐ 단원입니다. 테스트 이름과 설명은 주어지고, 본문은 여러분이 씁니다.
각 테스트의 docstring 이 "무엇을 확인해야 하는가"입니다. pytest.fail 줄을 지우고 그 내용을 코드로 옮기세요.
픽스처와 도우미는 완성되어 있으니 그대로 쓰면 됩니다.
"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from todo.api import create_app
from todo.auth import AuthError, UserStore, hash_password, hash_token, new_token, verify_password
from todo.repository import MemoryTaskRepository
from todo.service import TaskService


class FakeClock:
    """시간을 손으로 돌리는 가짜 시계. clock() 처럼 부를 수 있고 advance() 로 미래로 간다."""

    def __init__(self, start: datetime = datetime(2026, 3, 1, 9, 0)):
        self.now = start

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs) -> None:
        self.now += timedelta(**kwargs)


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def users(clock):
    return UserStore(clock=clock, token_ttl=timedelta(hours=1))


@pytest.fixture
def client(clock, users):
    return TestClient(create_app(TaskService(MemoryTaskRepository(), clock=clock), users))


def register_and_login(client, username: str, password: str = "correct horse battery") -> dict:
    """사용자를 만들고 로그인해 Authorization 헤더 딕셔너리를 돌려준다."""
    assert client.post("/auth/register", json={"username": username, "password": password}).status_code == 201
    token = client.post("/auth/login", json={"username": username, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- 비밀번호 해싱 ---------------------------------------------------------------


def test_hash_password_is_not_the_password():
    """hash_password 결과에 원문이 들어 있지 않고, 'scrypt$' 로 시작하며, 같은 비밀번호도 호출마다 다른 문자열이 나온다(salt)."""
    pytest.fail("아직 구현하지 않음")


def test_verify_password_accepts_correct_and_rejects_wrong():
    """verify_password(원문, 해시) 는 True, 다른 비밀번호나 형식이 깨진 문자열은 False."""
    pytest.fail("아직 구현하지 않음")


def test_hash_token_is_deterministic_and_token_is_random():
    """new_token() 은 두 번 부르면 다르고 충분히 길다(>= 32자). hash_token(t) 는 같은 t 에 항상 같은 값."""
    pytest.fail("아직 구현하지 않음")


# --- UserStore ------------------------------------------------------------------


def test_register_rejects_duplicate_and_short_password(users):
    """같은 이름 두 번 → ValueError. 8자 미만 비밀번호 → ValueError. 실패해도 사용자 수는 그대로."""
    pytest.fail("아직 구현하지 않음")


def test_login_returns_token_and_wrong_password_raises(users):
    """맞으면 문자열 토큰. 틀린 비밀번호와 없는 사용자는 **같은** AuthError 메시지(어느 쪽이 틀렸는지 새지 않게)."""
    pytest.fail("아직 구현하지 않음")


def test_token_expires_after_ttl(users, clock):
    """로그인 직후 user_for_token 은 사용자를 돌려주고, clock 을 61분 돌리면 AuthError."""
    pytest.fail("아직 구현하지 않음")


def test_store_keeps_only_token_hash(users):
    """UserStore 내부 어디에도 토큰 원문이 없어야 한다. (힌트: vars(users) 를 문자열로 만들어 토큰이 들어 있는지 보기)"""
    pytest.fail("아직 구현하지 않음")


# --- API: 인증 -------------------------------------------------------------------


def test_register_returns_201_without_password(client):
    """POST /auth/register → 201, 본문은 {id, username} 뿐. password 나 password_hash 는 절대 응답에 없다."""
    pytest.fail("아직 구현하지 않음")


def test_register_duplicate_returns_409(client):
    """같은 이름으로 두 번 등록 → 409, 봉투의 code 는 'username_taken'."""
    pytest.fail("아직 구현하지 않음")


def test_login_wrong_returns_401_with_www_authenticate(client):
    """틀린 비밀번호 → 401, code 'unauthorized', 응답 헤더 WWW-Authenticate: Bearer."""
    pytest.fail("아직 구현하지 않음")


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Basic abc"}, {"Authorization": "Bearer "}, {"Authorization": "Bearer 틀린토큰"}])
def test_tasks_require_bearer_token(client, headers):
    """토큰이 없거나 형식이 틀리거나 모르는 토큰이면 GET /tasks 는 401. /health 는 토큰 없이도 200."""
    pytest.fail("아직 구현하지 않음")


# --- API: 소유권 -----------------------------------------------------------------


def test_user_sees_only_own_tasks(client):
    """ann 이 2개, bob 이 1개 만들면 GET /tasks 는 각자 자기 것만. 응답에 owner_id 는 없다."""
    pytest.fail("아직 구현하지 않음")


def test_other_users_task_looks_like_it_does_not_exist(client):
    """bob 이 ann 의 할 일에 GET / POST complete / DELETE 를 보내면 모두 404 (403 이 아니다 — README 질문 2)."""
    pytest.fail("아직 구현하지 않음")


def test_expired_token_is_rejected_by_api(client, clock):
    """로그인 후 clock 을 2시간 돌리면 같은 헤더로 GET /tasks 가 401 '토큰이 만료되었습니다'."""
    pytest.fail("아직 구현하지 않음")


def test_openapi_documents_401(client):
    """/openapi.json 의 /tasks GET 응답에 '401' 이 있다. 호출자가 문서만 보고도 인증이 필요함을 안다."""
    pytest.fail("아직 구현하지 않음")
