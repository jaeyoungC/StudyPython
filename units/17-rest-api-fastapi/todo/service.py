"""서비스(service) 계층: 업무 규칙은 전부 여기에 있다.

- 저장 방법은 모른다 (TaskRepository 에 위임)
- 화면(CLI, HTTP)도 모른다 (입력은 파이썬 값, 출력은 Task 또는 예외)
- 현재 시각은 clock 으로 주입받는다. 테스트가 시간을 멈출 수 있어야 하기 때문이다.
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
        if not title.strip():
            raise ValueError("제목은 비어 있을 수 없습니다")
        if due is not None and due < self.today():
            raise ValueError(f"마감일 {due} 은(는) 오늘({self.today()})보다 앞설 수 없습니다")
        return self.repo.add(title, tags=tags, due=due)

    def get(self, task_id: int) -> Task:
        return self.repo.get(task_id)

    def complete(self, task_id: int) -> Task:
        """규칙: 이미 완료된 할 일은 AlreadyDoneError."""
        if self.repo.get(task_id).done:
            raise AlreadyDoneError(f"할 일 #{task_id} 은(는) 이미 완료되었습니다")
        return self.repo.complete(task_id)

    def remove(self, task_id: int) -> Task:
        return self.repo.remove(task_id)

    def list(self, done: bool | None = None) -> list[Task]:
        """done=None 전체, True 완료만, False 미완료만."""
        if done is None:
            return self.repo.all()
        if done is False:
            return self.repo.open_tasks()
        return [t for t in self.repo.all() if t.done]

    def by_tag(self, tag: str) -> list[Task]:
        return self.repo.by_tag(tag)

    def search(self, text: str) -> list[Task]:
        return self.repo.search(text)

    def overdue(self) -> list[Task]:
        """마감일이 지났는데 아직 끝내지 않은 할 일."""
        today = self.today()
        return [t for t in self.repo.open_tasks() if t.due is not None and t.due < today]
