"""백그라운드 워커 (20단원): 큐에서 이벤트를 꺼내 알림을 보내는 별도 스레드.

요청 스레드(API)는 큐에 넣고 바로 응답한다. 워커 스레드는 자기 속도로 꺼내 보낸다.
둘 사이의 완충 장치가 queue.Queue 다 (스레드 안전, 11단원의 잠금을 안에 품고 있다).

사용:
    worker = NotificationWorker(FakeNotifier())
    worker.start()
    service = TaskService(repo, events=worker.publish)
    ...
    worker.stop()          # 남은 것을 다 보내고 멈춘다
"""

from __future__ import annotations

import logging
import queue
import threading

from .events import Event
from .notifier import Notifier

log = logging.getLogger(__name__)

_STOP = object()  # 큐에 넣는 "이제 그만" 표시(센티널)


def format_message(event: Event) -> str:
    if event.type == "task.completed":
        return f"할 일 '{event.title}' 을(를) 완료했습니다"
    return f"{event.type}: {event.title}"


class NotificationWorker:
    def __init__(self, notifier: Notifier) -> None:
        self.notifier = notifier
        self.queue: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None
        self.processed = 0
        self.failed = 0

    # -- 생산자 쪽 (요청 스레드가 부른다) --------------------------------------

    def publish(self, event: Event) -> None:
        """넣고 바로 돌아온다. 이 함수가 느려지면 안 된다. 힌트: self.queue.put"""
        # TODO
        raise NotImplementedError

    # -- 소비자 쪽 (워커 스레드) --------------------------------------------

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, name="notification-worker", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        """무한 루프: queue.get() → _STOP 이면 return, 아니면 _handle. 어느 쪽이든 finally 에서 queue.task_done()."""
        # TODO
        raise NotImplementedError

    def _handle(self, event: Event) -> None:
        """한 건 처리. 실패해도 워커는 죽지 않는다 — 기록하고 다음 것으로 간다 (재시도는 25단원)."""
        # TODO
        raise NotImplementedError

    def join(self, timeout: float | None = None) -> bool:
        """큐가 빌 때까지 기다린다. 테스트가 '다 보냈는지' 확인할 때 쓴다. timeout 안에 비면 True."""
        done = threading.Event()

        def wait() -> None:
            self.queue.join()
            done.set()

        threading.Thread(target=wait, daemon=True).start()
        return done.wait(timeout)

    def stop(self, drain: bool = True) -> None:
        """drain=True 면 남은 이벤트를 다 처리한 뒤 멈춘다. False 면 지금 큐에 있는 것은 버린다.

        힌트: _STOP 을 큐에 넣고 스레드를 join. drain=False 면 그 전에 get_nowait 로 비우되 task_done 도 맞춰 부른다.
        """
        # TODO
        raise NotImplementedError
