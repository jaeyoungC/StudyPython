"""도메인 모델: Task, TaskList, TaskNotFoundError. (05단원까지의 완성본)"""

from dataclasses import asdict, dataclass, field
from typing import Iterator


class TaskNotFoundError(ValueError):
    """없는 id로 할 일을 찾았을 때."""


@dataclass
class Task:
    id: int
    title: str
    done: bool = False

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("제목이 비어 있습니다")

    def complete(self) -> None:
        if self.done:
            raise ValueError(f"#{self.id} 은 이미 완료되었습니다")
        self.done = True

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        if not isinstance(data, dict):
            raise ValueError(f"딕셔너리가 아닙니다: {data!r}")
        try:
            task_id, title = data["id"], data["title"]
        except KeyError as error:
            raise ValueError(f"필수 키가 없습니다: {error}") from error
        done = data.get("done", False)
        # bool 은 int 의 하위 타입이므로 id 검사에서 True/False 를 걸러낸다
        if not isinstance(task_id, int) or isinstance(task_id, bool):
            raise ValueError(f"id 는 정수여야 합니다: {task_id!r}")
        if not isinstance(title, str):
            raise ValueError(f"title 은 문자열이어야 합니다: {title!r}")
        if not isinstance(done, bool):
            raise ValueError(f"done 은 참/거짓이어야 합니다: {done!r}")
        return cls(id=task_id, title=title, done=done)


@dataclass
class TaskList:
    """메모리에 할 일을 보관하는 목록."""

    _tasks: list[Task] = field(default_factory=list)

    def add(self, title: str) -> Task:
        next_id = max((t.id for t in self._tasks), default=0) + 1
        task = Task(id=next_id, title=title)
        self._tasks.append(task)
        return task

    def get(self, task_id: int) -> Task:
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"#{task_id} 할 일이 없습니다")

    def find(self, title: str) -> Task | None:
        for task in self._tasks:
            if task.title == title:
                return task
        return None

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        task.complete()
        return task

    def remove(self, task_id: int) -> Task:
        task = self.get(task_id)
        self._tasks.remove(task)
        return task

    def all(self) -> list[Task]:
        return list(self._tasks)

    def open_tasks(self) -> list[Task]:
        return [t for t in self._tasks if not t.done]

    def __len__(self) -> int:
        return len(self._tasks)

    def __iter__(self) -> Iterator[Task]:
        return iter(self._tasks)
