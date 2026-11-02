"""할 일 도메인 모델 (05단원 완성본).

- Task: 할 일 하나. 제목은 앞뒤 공백을 제거하고, 비어 있으면 ValueError. 태그는 normalize_tags 로 정리한다.
- TaskNotFoundError: 없는 id를 요청했을 때. ValueError의 하위 클래스라서
  `except ValueError` 로도 잡힌다.
- TaskList: 메모리에만 보관하는 할 일 목록. 저장소(JSON, SQLite)는 이 클래스와
  같은 메서드 이름을 쓴다.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Iterator


def normalize_tags(tags: Iterable[str]) -> list[str]:
    """태그 목록을 표준 모양으로: 앞뒤 공백 제거, 빈 문자열 제외, 중복 제거, 가나다·알파벳 순 정렬.

    저장소가 무엇이든(메모리, JSON, SQLite) 같은 태그 목록은 같은 리스트로 비교되게 하려는 규칙이다.
    """
    cleaned = {str(tag).strip() for tag in tags}
    cleaned.discard("")
    return sorted(cleaned)


class TaskNotFoundError(ValueError):
    """요청한 id의 할 일이 없을 때 던지는 예외."""

    def __init__(self, task_id: int) -> None:
        super().__init__(f"할 일 #{task_id} 이(가) 없습니다")
        self.task_id = task_id


@dataclass
class Task:
    """할 일 하나.

    `title` 은 생성 시점에 앞뒤 공백을 제거하고, 비어 있으면 ValueError 를 던진다.
    (`__post_init__` 은 dataclass 가 `__init__` 을 끝낸 직후 호출하는 훅이다.)
    """

    id: int
    title: str
    done: bool = False
    tags: list[str] = field(default_factory=list)  # 09단원: 앞뒤 공백 제거, 빈 값 제외, 중복 제거, 정렬

    def __post_init__(self) -> None:
        if not isinstance(self.title, str):
            raise ValueError("제목은 문자열이어야 합니다")
        title = self.title.strip()
        if not title:
            raise ValueError("제목은 비어 있을 수 없습니다")
        self.title = title
        self.tags = normalize_tags(self.tags)

    def to_dict(self) -> dict[str, Any]:
        """JSON 으로 저장하기 좋은 딕셔너리로 바꾼다."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """`to_dict` 의 역변환. 필수 키가 없으면 KeyError, 값이 이상하면 ValueError."""
        return cls(
            id=int(data["id"]),
            title=data["title"],
            done=bool(data.get("done", False)),
            tags=list(data.get("tags", [])),  # 09단원 이전에 저장한 파일에는 tags 가 없다
        )


class TaskList:
    """메모리에 보관하는 할 일 목록.

    id 는 "현재 가장 큰 id + 1" 로 정한다(삭제 뒤 추가해도 기존 id 와 겹치지 않는다).
    """

    def __init__(self, tasks: Iterable[Task] = ()) -> None:
        self._tasks: list[Task] = list(tasks)

    def add(self, title: str, tags: Iterable[str] = ()) -> Task:
        """새 할 일을 추가하고 돌려준다. 제목이 비어 있으면 ValueError."""
        new_id = max((task.id for task in self._tasks), default=0) + 1
        task = Task(id=new_id, title=title, tags=list(tags))
        self._tasks.append(task)
        return task

    def by_tag(self, tag: str) -> list[Task]:
        """주어진 태그가 붙은 할 일만 새 리스트로 돌려준다."""
        tag = tag.strip()
        return [task for task in self._tasks if tag in task.tags]

    def get(self, task_id: int) -> Task:
        """id 로 할 일을 찾는다. 없으면 TaskNotFoundError."""
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(task_id)

    def complete(self, task_id: int) -> Task:
        """할 일을 완료 처리한다. 이미 완료면 ValueError."""
        task = self.get(task_id)
        if task.done:
            raise ValueError(f"할 일 #{task_id} 은(는) 이미 완료되었습니다")
        task.done = True
        return task

    def remove(self, task_id: int) -> Task:
        """할 일을 지우고 지운 할 일을 돌려준다."""
        task = self.get(task_id)
        self._tasks.remove(task)
        return task

    def all(self) -> list[Task]:
        """모든 할 일을 새 리스트로 돌려준다."""
        return list(self._tasks)

    def open_tasks(self) -> list[Task]:
        """아직 끝나지 않은(done=False) 할 일만 새 리스트로 돌려준다."""
        return [task for task in self._tasks if not task.done]

    def __len__(self) -> int:
        return len(self._tasks)

    def __iter__(self) -> Iterator[Task]:
        return iter(self.all())
