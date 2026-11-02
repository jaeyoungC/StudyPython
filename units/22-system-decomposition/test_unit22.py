"""22단원 테스트 뼈대. 실행: pytest units/22-system-decomposition

두 서비스를 한 테스트 프로세스 안에서 돌립니다. 트릭 하나: FastAPI 의 TestClient 는 httpx.Client 의 자식이라서
HttpNotifier(client=TestClient(notifier_app)) 처럼 꽂으면 진짜 소켓 없이 "HTTP 로 다른 서비스를 부르는" 경로를 그대로 지나갑니다.
진짜 두 프로세스로 띄워 보는 것은 README 의 손 실험입니다.
"""

import threading
from datetime import datetime

import httpx
import pytest
from fastapi.testclient import TestClient

from notifier.app import NotificationStore, create_notifier_app
from todo.api import create_app
from todo.auth import UserStore
from todo.events import Event
from todo.notifier import HttpNotifier
from todo.repository import MemoryTaskRepository
from todo.service import TaskService
from todo.worker import NotificationWorker

CLOCK = lambda: datetime(2026, 3, 1, 9, 0)  # noqa: E731


@pytest.fixture
def notifier_store():
    return NotificationStore(clock=CLOCK)


@pytest.fixture
def notifier_client(notifier_store):
    return TestClient(create_notifier_app(notifier_store))


@pytest.fixture
def http_notifier(notifier_client):
    return HttpNotifier("http://notifier", client=notifier_client)


@pytest.fixture
def worker(http_notifier):
    worker = NotificationWorker(http_notifier)
    worker.start()
    yield worker
    worker.stop(drain=False)


@pytest.fixture
def todo_client(worker):
    service = TaskService(MemoryTaskRepository(), clock=CLOCK, events=worker.publish)
    client = TestClient(create_app(service, UserStore(clock=CLOCK)))
    client.post("/auth/register", json={"username": "ann", "password": "correct horse battery"})
    token = client.post("/auth/login", json={"username": "ann", "password": "correct horse battery"}).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


class DeadTransport(httpx.BaseTransport):
    """연결이 안 되는 알림 서비스를 흉내 내는 테스트 대역(stub). 모든 요청에 ConnectError."""

    def handle_request(self, request):
        raise httpx.ConnectError("connection refused (가짜)")


# --- 알림 서비스 자체 ------------------------------------------------------------------


def test_notifier_service_accepts_and_lists(notifier_client):
    """POST /notifications {user_id: 1, message: 'x'} → 202 {"id": 1}. GET /notifications → 1건, GET ?user_id=2 → 0건."""
    pytest.fail("아직 구현하지 않음")


def test_notifier_service_rejects_empty_message(notifier_client):
    """message 가 빈 문자열이면 422."""
    pytest.fail("아직 구현하지 않음")


# --- HttpNotifier: 서비스 사이의 HTTP 호출 ----------------------------------------------------


def test_http_notifier_posts_to_notifier_service(http_notifier, notifier_store):
    """http_notifier.send(1, '안녕') 뒤 notifier_store.list(1) 에 '안녕' 이 있다."""
    pytest.fail("아직 구현하지 않음")


def test_http_notifier_raises_when_service_is_down():
    """HttpNotifier(client=httpx.Client(transport=DeadTransport())) 의 send 는 httpx.HTTPError 를 던진다. 삼키지 않는다."""
    pytest.fail("아직 구현하지 않음")


def test_http_notifier_raises_on_5xx(notifier_store):
    """알림 서비스가 500 을 주면(예: 항상 raise 하는 가짜 앱을 TestClient(raise_server_exceptions=False) 로) send 가 예외를 던진다."""
    pytest.fail("아직 구현하지 않음")


# --- 두 서비스를 함께: 분산의 비용 ---------------------------------------------------------


def test_complete_in_todo_service_reaches_notifier_service(todo_client, worker, notifier_store):
    """POST /tasks → POST /tasks/1/complete 가 200 → worker.join(2) → notifier_store.list() 에 제목이 든 메시지 1건."""
    pytest.fail("아직 구현하지 않음")


def test_todo_service_still_works_when_notifier_is_down():
    """DeadTransport 를 쓰는 HttpNotifier + 워커로 할 일 서비스를 만들어도 complete 는 200 이고, join 후 worker.failed == 1. 부분 실패(partial failure)는 격리된다."""
    pytest.fail("아직 구현하지 않음")


def test_notifier_service_knows_nothing_about_tasks(notifier_store):
    """notifier_store 에 저장된 항목에는 task_id 나 title 필드가 없다 (message 문자열 안에만 있다). 데이터 소유권: 알림 서비스는 할 일 테이블을 모른다."""
    pytest.fail("아직 구현하지 않음")


def test_http_call_is_slower_than_in_process_call(http_notifier, notifier_store):
    """같은 메시지 200건을 FakeNotifier.send 와 HttpNotifier.send 로 보내는 시간을 perf_counter 로 재면 HTTP 쪽이 더 느리다 (몇 배인지 NOTES.md 에). 단언은 '더 느리다'만."""
    pytest.fail("아직 구현하지 않음")


def test_timeout_is_always_set(http_notifier):
    """HttpNotifier 의 timeout 은 None 이 아니고 양수다. 기본값으로 만든 HttpNotifier('http://x') 의 client.timeout 도 설정되어 있다."""
    pytest.fail("아직 구현하지 않음")
