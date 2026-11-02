"""서비스(service) 계층: 업무 규칙은 전부 여기에 있다.

- 저장 방법은 모른다 (TaskRepository 에 위임)
- 화면(CLI, HTTP)도 모른다 (입력은 파이썬 값, 출력은 Task 또는 예외)
- 현재 시각은 clock 으로 주입받는다. 테스트가 시간을 멈출 수 있어야 하기 때문이다.
- 20단원: events 를 주면 complete() 뒤에 Event("task.completed") 를 발행한다. 발송은 워커가 한다.
- 19단원: cache 를 주면 list() 결과를 (owner_id, done) 별로 기억하고, 쓰기(add/complete/remove)마다 전부 비운다.
  "무엇을 캐시하는가"의 답: 자주 읽히고(목록), 계산이 비싸질 수 있고(리포지토리 전체 훑기), 바뀌는 순간을 우리가 아는 것.
- 18단원: owner_id 를 주면 "그 사용자의 할 일"만 보이고 만들어진다. None 이면 소유권 검사를 하지 않는다(CLI, 옛 테스트).
  남의 할 일은 403 이 아니라 **없는 것처럼**(TaskNotFoundError) 다룬다. 존재 여부 자체를 새지 않게 하기 위해서다.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime

from .cache import MemoryCache
from .events import Event
from .models import Task, TaskNotFoundError
from .repository import TaskRepository


class AlreadyDoneError(ValueError):
    """이미 완료된 할 일을 다시 완료하려 할 때."""


class TaskService:
    def __init__(
        self,
        repo: TaskRepository,
        clock: Callable[[], datetime] = datetime.now,
        cache: MemoryCache | None = None,
        events: Callable[[Event], None] | None = None,
    ) -> None:
        self.repo = repo
        self.clock = clock
        self.cache = cache  # None 이면 캐시 없음. 동작은 같고 속도만 다르다 — 그래야 캐시다.
        self.events = events  # 이벤트를 받을 함수(보통 NotificationWorker.publish). None 이면 발행하지 않는다.

    # -- 캐시 ------------------------------------------------------------

    LIST_PREFIX = "list:"

    def _invalidate(self) -> None:
        """쓰기가 일어났다. 목록 캐시는 전부 의심스럽다 → 전부 버린다. (세분화는 측정한 뒤에, README 질문 3)"""
        if self.cache is not None:
            self.cache.delete_prefix(self.LIST_PREFIX)

    def today(self) -> date:
        return self.clock().date()

    # -- 소유권 ------------------------------------------------------------

    @staticmethod
    def _owned(task: Task, owner_id: int | None) -> bool:
        return owner_id is None or task.owner_id == owner_id

    def _visible(self, tasks: list[Task], owner_id: int | None) -> list[Task]:
        return [t for t in tasks if self._owned(t, owner_id)]

    # -- 규칙 ------------------------------------------------------------

    def add(
        self, title: str, tags: Iterable[str] = (), due: date | None = None, owner_id: int | None = None
    ) -> Task:
        """규칙: 빈 제목 금지(ValueError), 과거 마감일 금지(ValueError)."""
        if not title.strip():
            raise ValueError("제목은 비어 있을 수 없습니다")
        if due is not None and due < self.today():
            raise ValueError(f"마감일 {due} 은(는) 오늘({self.today()})보다 앞설 수 없습니다")
        task = self.repo.add(title, tags=tags, due=due, owner_id=owner_id)
        self._invalidate()
        return task

    def get(self, task_id: int, owner_id: int | None = None) -> Task:
        task = self.repo.get(task_id)
        if not self._owned(task, owner_id):
            raise TaskNotFoundError(f"할 일 #{task_id} 이(가) 없습니다")
        return task

    def complete(self, task_id: int, owner_id: int | None = None) -> Task:
        """규칙: 이미 완료된 할 일은 AlreadyDoneError."""
        if self.get(task_id, owner_id).done:
            raise AlreadyDoneError(f"할 일 #{task_id} 은(는) 이미 완료되었습니다")
        task = self.repo.complete(task_id)
        self._invalidate()
        # TODO: self.events 가 있으면 Event(type="task.completed", task_id=..., owner_id=..., title=...) 를 발행한다.
        #       발행은 "함수 호출 한 번"이다. 발송이 아니다. 여기서 알림을 직접 보내면 complete 가 느려지고 실패할 수 있다.
        return task

    def remove(self, task_id: int, owner_id: int | None = None) -> Task:
        self.get(task_id, owner_id)
        task = self.repo.remove(task_id)
        self._invalidate()
        return task

    def list(self, done: bool | None = None, owner_id: int | None = None) -> list[Task]:
        """done=None 전체, True 완료만, False 미완료만. 캐시가 있으면 (owner_id, done) 별로 기억한다."""
        key = f"{self.LIST_PREFIX}{owner_id}:{done}"
        if self.cache is not None:
            cached = self.cache.get(key)
            if cached is not None:
                return list(cached)  # 호출자가 결과를 바꿔도 캐시는 안전하게: 새 리스트
        if done is None:
            tasks = self.repo.all()
        elif done is False:
            tasks = self.repo.open_tasks()
        else:
            tasks = [t for t in self.repo.all() if t.done]
        result = self._visible(tasks, owner_id)
        if self.cache is not None:
            self.cache.set(key, list(result))
        return result

    def by_tag(self, tag: str, owner_id: int | None = None) -> list[Task]:
        return self._visible(self.repo.by_tag(tag), owner_id)

    def search(self, text: str, owner_id: int | None = None) -> list[Task]:
        return self._visible(self.repo.search(text), owner_id)

    def overdue(self, owner_id: int | None = None) -> list[Task]:
        """마감일이 지났는데 아직 끝내지 않은 할 일."""
        today = self.today()
        return [t for t in self._visible(self.repo.open_tasks(), owner_id) if t.due is not None and t.due < today]
