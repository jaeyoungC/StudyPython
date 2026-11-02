"""서비스(service) 계층: 업무 규칙은 전부 여기에 있다.

- 저장 방법은 모른다 (TaskRepository 에 위임)
- 화면(CLI, HTTP)도 모른다 (입력은 파이썬 값, 출력은 Task 또는 예외)
- 현재 시각은 clock 으로 주입받는다. 테스트가 시간을 멈출 수 있어야 하기 때문이다.

과제: TODO 를 채우세요. "오늘"이 필요하면 datetime.now() 가 아니라 self.today() 를 쓰세요.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime

from .models import Task
from .repository import TaskRepository


class AlreadyDoneError(ValueError):
    """이미 완료된 할 일을 다시 완료하려 할 때."""


class TaskService:
    def __init__(self, repo: TaskRepository, clock: Callable[[], datetime] = datetime.now) -> None:
        self.repo = repo
        self.clock = clock

    def today(self) -> date:
        return self.clock().date()

    def add(self, title: str, tags: Iterable[str] = (), due: date | None = None) -> Task:
        """규칙: 빈 제목 금지(ValueError), 과거 마감일 금지(ValueError)."""
        # TODO
        raise NotImplementedError

    def get(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def complete(self, task_id: int) -> Task:
        """규칙: 이미 완료된 할 일은 AlreadyDoneError."""
        # TODO
        raise NotImplementedError

    def remove(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def list(self, done: bool | None = None) -> list[Task]:
        """done=None 전체, True 완료만, False 미완료만."""
        # TODO
        raise NotImplementedError

    def by_tag(self, tag: str) -> list[Task]:
        # TODO
        raise NotImplementedError

    def search(self, text: str) -> list[Task]:
        # TODO
        raise NotImplementedError

    def overdue(self) -> list[Task]:
        """마감일이 지났는데 아직 끝내지 않은 할 일."""
        # TODO
        raise NotImplementedError
