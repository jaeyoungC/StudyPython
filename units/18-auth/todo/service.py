"""서비스(service) 계층: 업무 규칙은 전부 여기에 있다.

- 저장 방법은 모른다 (TaskRepository 에 위임)
- 화면(CLI, HTTP)도 모른다 (입력은 파이썬 값, 출력은 Task 또는 예외)
- 현재 시각은 clock 으로 주입받는다. 테스트가 시간을 멈출 수 있어야 하기 때문이다.
- 18단원: owner_id 를 주면 "그 사용자의 할 일"만 보이고 만들어진다. None 이면 소유권 검사를 하지 않는다(CLI, 옛 테스트).
  남의 할 일은 403 이 아니라 **없는 것처럼**(TaskNotFoundError) 다룬다. 존재 여부 자체를 새지 않게 하기 위해서다.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime

from .models import Task, TaskNotFoundError
from .repository import TaskRepository


class AlreadyDoneError(ValueError):
    """이미 완료된 할 일을 다시 완료하려 할 때."""


class TaskService:
    def __init__(self, repo: TaskRepository, clock: Callable[[], datetime] = datetime.now) -> None:
        self.repo = repo
        self.clock = clock

    def today(self) -> date:
        return self.clock().date()

    # -- 소유권 ------------------------------------------------------------

    @staticmethod
    def _owned(task: Task, owner_id: int | None) -> bool:
        """owner_id 가 None 이면 항상 True(검사 안 함), 아니면 task.owner_id 와 같아야 True."""
        # TODO: 지금은 누구나 모든 할 일을 본다(17단원 상태). 소유권 규칙으로 바꾸세요.
        return True

    def _visible(self, tasks: list[Task], owner_id: int | None) -> list[Task]:
        """owner_id 가 볼 수 있는 것만 남긴 새 리스트."""
        # TODO: _owned 로 거른다.
        return list(tasks)

    # -- 규칙 ------------------------------------------------------------

    def add(
        self, title: str, tags: Iterable[str] = (), due: date | None = None, owner_id: int | None = None
    ) -> Task:
        """규칙: 빈 제목 금지(ValueError), 과거 마감일 금지(ValueError)."""
        if not title.strip():
            raise ValueError("제목은 비어 있을 수 없습니다")
        if due is not None and due < self.today():
            raise ValueError(f"마감일 {due} 은(는) 오늘({self.today()})보다 앞설 수 없습니다")
        return self.repo.add(title, tags=tags, due=due, owner_id=owner_id)

    def get(self, task_id: int, owner_id: int | None = None) -> Task:
        task = self.repo.get(task_id)
        if not self._owned(task, owner_id):
            raise TaskNotFoundError(f"할 일 #{task_id} 이(가) 없습니다")
        return task

    def complete(self, task_id: int, owner_id: int | None = None) -> Task:
        """규칙: 이미 완료된 할 일은 AlreadyDoneError."""
        if self.get(task_id, owner_id).done:
            raise AlreadyDoneError(f"할 일 #{task_id} 은(는) 이미 완료되었습니다")
        return self.repo.complete(task_id)

    def remove(self, task_id: int, owner_id: int | None = None) -> Task:
        self.get(task_id, owner_id)
        return self.repo.remove(task_id)

    def list(self, done: bool | None = None, owner_id: int | None = None) -> list[Task]:
        """done=None 전체, True 완료만, False 미완료만."""
        if done is None:
            tasks = self.repo.all()
        elif done is False:
            tasks = self.repo.open_tasks()
        else:
            tasks = [t for t in self.repo.all() if t.done]
        return self._visible(tasks, owner_id)

    def by_tag(self, tag: str, owner_id: int | None = None) -> list[Task]:
        return self._visible(self.repo.by_tag(tag), owner_id)

    def search(self, text: str, owner_id: int | None = None) -> list[Task]:
        return self._visible(self.repo.search(text), owner_id)

    def overdue(self, owner_id: int | None = None) -> list[Task]:
        """마감일이 지났는데 아직 끝내지 않은 할 일."""
        today = self.today()
        return [t for t in self._visible(self.repo.open_tasks(), owner_id) if t.due is not None and t.due < today]
