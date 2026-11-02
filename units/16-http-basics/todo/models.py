"""도메인 모델: Task, TaskNotFoundError, TaskList(메모리 저장)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date


class TaskNotFoundError(ValueError):
    """없는 id를 요청했을 때."""


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    tags: list[str] = field(default_factory=list)
    due: date | None = None

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("제목은 비어 있을 수 없습니다")
        self.tags = [t.strip() for t in self.tags if t.strip()]

    def to_dict(self) -> dict:
        """JSON으로 저장할 수 있는 딕셔너리. date는 ISO 문자열로."""
        data = asdict(self)
        data["due"] = self.due.isoformat() if self.due else None
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        due = data.get("due")
        return cls(
            id=int(data["id"]),
            title=data["title"],
            done=bool(data.get("done", False)),
            tags=list(data.get("tags", [])),
            due=date.fromisoformat(due) if due else None,
        )


class TaskList:
    """메모리에만 저장하는 할 일 목록."""

    def __init__(self, tasks: list[Task] | None = None) -> None:
        self._tasks: list[Task] = list(tasks or [])

    def add(self, title: str, tags: tuple[str, ...] | list[str] = (), due: date | None = None) -> Task:
        next_id = max((t.id for t in self._tasks), default=0) + 1
        task = Task(id=next_id, title=title, tags=list(tags), due=due)
        self._tasks.append(task)
        return task

    def get(self, task_id: int) -> Task:
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"할 일 #{task_id} 이(가) 없습니다")

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        if task.done:
            raise ValueError(f"할 일 #{task_id} 은(는) 이미 완료되었습니다")
        task.done = True
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

    def __iter__(self):
        return iter(self.all())
