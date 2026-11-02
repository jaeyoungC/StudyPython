"""2주차: 할 일을 클래스로 표현하기.

TODO를 채워 `pytest weeks/week02` 를 통과시키세요.
"""

from dataclasses import dataclass, field


class TaskNotFoundError(ValueError):
    """없는 id로 할 일을 찾았을 때 발생한다."""


@dataclass
class Task:
    id: int
    title: str
    done: bool = False

    def __post_init__(self) -> None:
        """만들어질 때 title 앞뒤 공백을 제거하고, 비어 있으면 ValueError."""
        # TODO
        raise NotImplementedError

    def complete(self) -> None:
        """완료 처리한다. 이미 완료된 할 일이면 ValueError."""
        # TODO
        raise NotImplementedError


@dataclass
class TaskList:
    _tasks: list[Task] = field(default_factory=list)

    def add(self, title: str) -> Task:
        """새 Task를 만들어 추가하고 반환한다. id는 최대 id + 1 (비어 있으면 1)."""
        # TODO
        raise NotImplementedError

    def get(self, task_id: int) -> Task:
        """id로 찾아 반환한다. 없으면 TaskNotFoundError."""
        # TODO
        raise NotImplementedError

    def complete(self, task_id: int) -> Task:
        """해당 할 일을 완료 처리하고 반환한다."""
        # TODO
        raise NotImplementedError

    def remove(self, task_id: int) -> Task:
        """해당 할 일을 지우고 반환한다."""
        # TODO
        raise NotImplementedError

    def open_tasks(self) -> list[Task]:
        """미완료 할 일을 새 리스트로 반환한다."""
        # TODO
        raise NotImplementedError

    def __len__(self) -> int:
        # TODO
        raise NotImplementedError
