"""05단원: dataclass, 타입 힌트, 직렬화.

TODO를 채워 `pytest units/05-dataclasses` 를 통과시키세요.
"""

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
        """title 앞뒤 공백을 제거하고, 비어 있으면 ValueError."""
        # TODO
        raise NotImplementedError

    def complete(self) -> None:
        """완료 처리. 이미 완료면 ValueError."""
        # TODO
        raise NotImplementedError

    def to_dict(self) -> dict:
        """{"id": ..., "title": ..., "done": ...} 형태의 딕셔너리. 힌트: asdict"""
        # TODO
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """딕셔너리에서 Task를 만든다.

        - "id"(int), "title"(str) 는 필수, "done"(bool) 은 없으면 False
        - 키가 빠졌거나 타입이 맞지 않으면 ValueError
        """
        # TODO
        raise NotImplementedError


@dataclass
class TaskList:
    _tasks: list[Task] = field(default_factory=list)

    def add(self, title: str) -> Task:
        # TODO
        raise NotImplementedError

    def get(self, task_id: int) -> Task:
        """없으면 TaskNotFoundError."""
        # TODO
        raise NotImplementedError

    def find(self, title: str) -> Task | None:
        """제목이 정확히 같은 첫 할 일. 없으면 None."""
        # TODO
        raise NotImplementedError

    def complete(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def remove(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def all(self) -> list[Task]:
        # TODO
        raise NotImplementedError

    def open_tasks(self) -> list[Task]:
        # TODO
        raise NotImplementedError

    def __len__(self) -> int:
        # TODO
        raise NotImplementedError

    def __iter__(self) -> Iterator[Task]:
        """for task in tasks: 가 되게 한다. 힌트: iter(self._tasks) 또는 yield from"""
        # TODO
        raise NotImplementedError
