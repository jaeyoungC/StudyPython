"""04단원: 할 일을 클래스로 표현하기 (dataclass 없이).

TODO를 채워 `pytest units/04-classes` 를 통과시키세요.
"""


class TaskNotFoundError(ValueError):
    """없는 id로 할 일을 찾았을 때. ValueError를 상속하므로 except ValueError로도 잡힌다."""


class Task:
    """할 일 하나. 속성: id(int), title(str), done(bool)."""

    def __init__(self, id: int, title: str, done: bool = False) -> None:
        """title 앞뒤 공백을 제거해 저장하고, 비어 있으면 ValueError."""
        # TODO: self.id, self.title, self.done 을 채우세요
        raise NotImplementedError

    def complete(self) -> None:
        """완료 처리. 이미 완료된 할 일이면 ValueError."""
        # TODO
        raise NotImplementedError


class TaskList:
    """할 일 목록. 내부 리스트 self._tasks 는 밖에서 직접 만지지 않는다는 약속."""

    def __init__(self) -> None:
        self._tasks: list[Task] = []

    def add(self, title: str) -> Task:
        """새 Task를 만들어 추가하고 반환. id는 최대 id + 1 (비어 있으면 1)."""
        # TODO
        raise NotImplementedError

    def get(self, task_id: int) -> Task:
        """id로 찾아 반환. 없으면 TaskNotFoundError."""
        # TODO
        raise NotImplementedError

    def complete(self, task_id: int) -> Task:
        """해당 할 일을 완료 처리하고 반환."""
        # TODO
        raise NotImplementedError

    def remove(self, task_id: int) -> Task:
        """해당 할 일을 지우고 반환."""
        # TODO
        raise NotImplementedError

    def all(self) -> list[Task]:
        """전체 할 일을 새 리스트로 반환."""
        # TODO
        raise NotImplementedError

    def open_tasks(self) -> list[Task]:
        """미완료 할 일만 새 리스트로 반환."""
        # TODO
        raise NotImplementedError

    def count(self) -> int:
        """할 일 개수."""
        # TODO
        raise NotImplementedError
