"""20단원 테스트 뼈대. 실행: pytest units/20-async-and-background-jobs

◐ 단원: docstring 이 명세, 본문은 여러분이 씁니다.
시간을 재는 테스트는 느슨한 상한(예: 0.05초짜리 5개가 0.2초 안에)을 쓰세요. 느린 CI 에서도 통과해야 합니다.
"""

import inspect
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from todo.api import create_app
from todo.async_demo import run_concurrent, run_concurrent_but_blocking, run_sequential, timed
from todo.auth import UserStore
from todo.events import Event
from todo.notifier import FakeNotifier
from todo.repository import MemoryTaskRepository
from todo.service import TaskService
from todo.worker import NotificationWorker, format_message

CLOCK = lambda: datetime(2026, 3, 1, 9, 0)  # noqa: E731


@pytest.fixture
def notifier():
    return FakeNotifier()


@pytest.fixture
def worker(notifier):
    worker = NotificationWorker(notifier)
    worker.start()
    yield worker
    worker.stop(drain=False)  # 테스트가 끝나면 남은 것은 버리고 스레드를 정리한다


@pytest.fixture
def service(worker):
    return TaskService(MemoryTaskRepository(), clock=CLOCK, events=worker.publish)


# --- asyncio: 언제 빨라지고 언제 아닌가 -----------------------------------------------


def test_concurrent_is_faster_than_sequential():
    """5개 × 0.05초: run_sequential 은 0.2초 이상, run_concurrent 는 0.15초 미만. 결과 리스트는 둘 다 names 순서."""
    pytest.fail("아직 구현하지 않음")


def test_blocking_inside_async_does_not_speed_up():
    """run_concurrent_but_blocking 은 gather 를 써도 0.2초 이상 걸린다. time.sleep 이 루프를 멈추기 때문."""
    pytest.fail("아직 구현하지 않음")


def test_health_is_an_async_endpoint():
    """create_app 의 /health 경로 함수는 inspect.iscoroutinefunction 이 True. 다른 경로(/tasks)는 False (동기 서비스를 부르므로)."""
    pytest.fail("아직 구현하지 않음")


# --- 이벤트 발행: 서비스는 보내지 않고 알리기만 한다 ------------------------------------


def test_complete_publishes_event_without_sending(service, notifier):
    """events 에 기록용 리스트.append 를 꽂은 서비스로 complete 하면 Event(type='task.completed', task_id, owner_id, title) 가 한 번 발행된다. add 나 remove 는 발행하지 않는다."""
    pytest.fail("아직 구현하지 않음")


def test_service_without_events_still_works():
    """events=None 인 서비스의 complete 는 그대로 동작한다 (알림은 선택 기능)."""
    pytest.fail("아직 구현하지 않음")


def test_format_message_mentions_title():
    """format_message(Event('task.completed', 1, 1, '산책')) 에 '산책' 이 들어 있다."""
    pytest.fail("아직 구현하지 않음")


# --- 워커: 큐에서 꺼내 보낸다 -------------------------------------------------------------


def test_worker_sends_published_events(service, worker, notifier):
    """할 일 2개를 완료하고 worker.join(timeout=2) 가 True 이면 notifier.sent 에 2건, 각각 (owner_id, 메시지)."""
    pytest.fail("아직 구현하지 않음")


def test_worker_survives_a_failing_send(worker):
    """FakeNotifier(fail_times=1) 를 쓰는 워커에 이벤트 3개를 publish 하면 join 후 processed=2, failed=1, 워커 스레드는 살아 있다."""
    pytest.fail("아직 구현하지 않음")


def test_publish_returns_immediately_even_if_notifier_is_slow():
    """send 가 0.2초 걸리는 느린 notifier 라도 publish 10번은 0.05초 안에 끝난다. (perf_counter 로 재기)"""
    pytest.fail("아직 구현하지 않음")


def test_stop_with_drain_sends_everything(notifier):
    """start 없이 publish 3번 → start → stop(drain=True) 하면 sent 가 3건. stop 뒤 start 를 다시 부르면 새 스레드로 또 동작한다."""
    pytest.fail("아직 구현하지 않음")


def test_stop_without_drain_discards_queue(notifier):
    """publish 3번 뒤 start 하지 않고 stop(drain=False) 를 불러도 멈추지 않고(스레드 없음), start → stop(drain=False) 는 남은 것을 버려 sent 가 비어 있을 수 있다. 큐 길이는 0."""
    pytest.fail("아직 구현하지 않음")


# --- API 와 함께 -------------------------------------------------------------------


def test_complete_via_api_triggers_notification(service, worker, notifier):
    """가입·로그인 → POST /tasks → POST /tasks/1/complete 가 200 으로 **즉시** 돌아오고, join 후 notifier.sent 에 그 사용자 id 와 제목이 있다."""
    pytest.fail("아직 구현하지 않음")
