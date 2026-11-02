"""15단원 테스트. 실행: pytest units/15-layers-and-repository

핵심은 하나입니다: 같은 테스트가 세 리포지토리에서 모두 통과해야 한다.
`repo` 픽스처가 params 로 세 구현을 차례로 만들어 주고, 서비스 테스트는 그 위에서 돕니다.
"""

import sqlite3
from datetime import date, datetime

import pytest

from todo.models import Task, TaskNotFoundError
from todo.repository import JsonTaskRepository, MemoryTaskRepository, SqliteTaskRepository
from todo.service import AlreadyDoneError, TaskService

FIXED_NOW = datetime(2026, 3, 1, 9, 0)


def fixed_clock() -> datetime:
    """항상 2026-03-01 09:00 을 돌려주는 가짜 시계. 테스트가 '오늘'을 통제한다."""
    return FIXED_NOW


# 픽스처에 params 를 주면 이 픽스처를 쓰는 모든 테스트가 param 수만큼 반복된다.
@pytest.fixture(params=["memory", "json", "sqlite"])
def repo(request, tmp_path):
    # yield 를 쓰는 픽스처는 모든 경로에서 yield 해야 한다. yield 뒤는 테스트가 끝난 뒤 실행된다(정리).
    if request.param == "memory":
        yield MemoryTaskRepository()
    elif request.param == "json":
        yield JsonTaskRepository(tmp_path / "tasks.json")
    else:
        conn = sqlite3.connect(":memory:")
        yield SqliteTaskRepository(conn)
        conn.close()


@pytest.fixture
def service(repo):
    return TaskService(repo, clock=fixed_clock)


# --- 리포지토리: 세 구현이 같은 계약을 지키는가 -----------------------------


def test_repo_add_and_get(repo):
    task = repo.add("SQL 공부", tags=["study"], due=date(2026, 3, 10))
    assert task.id == 1
    fetched = repo.get(1)
    assert (fetched.title, fetched.tags, fetched.due, fetched.done) == ("SQL 공부", ["study"], date(2026, 3, 10), False)


def test_repo_get_missing_raises(repo):
    with pytest.raises(TaskNotFoundError):
        repo.get(99)


def test_repo_complete_and_open_tasks(repo):
    repo.add("a")
    repo.add("b")
    assert repo.complete(1).done is True
    assert [t.id for t in repo.open_tasks()] == [2]
    assert [t.id for t in repo.all()] == [1, 2]


def test_repo_remove(repo):
    repo.add("a")
    repo.add("b")
    assert repo.remove(1).title == "a"
    assert [t.id for t in repo.all()] == [2]
    with pytest.raises(TaskNotFoundError):
        repo.get(1)


def test_repo_by_tag(repo):
    repo.add("a", tags=["home"])
    repo.add("b", tags=["work", "home"])
    repo.add("c")
    assert [t.id for t in repo.by_tag("home")] == [1, 2]
    assert repo.by_tag("없는태그") == []


def test_repo_search_matches_word_in_title(repo):
    repo.add("SQL 공부")
    repo.add("산책")
    repo.add("영어 공부")
    assert sorted(t.id for t in repo.search("공부")) == [1, 3]
    assert repo.search("없는말") == []


def test_repo_returns_new_lists(repo):
    repo.add("a")
    first = repo.all()
    first.clear()
    assert len(repo.all()) == 1  # 호출한 쪽이 지워도 저장소는 안전해야 한다


def test_json_repo_persists_between_instances(tmp_path):
    """JSON 리포지토리는 객체를 새로 만들어도 파일에서 다시 읽어야 한다."""
    path = tmp_path / "tasks.json"
    JsonTaskRepository(path).add("a")
    assert [t.title for t in JsonTaskRepository(path).all()] == ["a"]


# --- 서비스: 규칙은 저장소와 무관하게 같아야 한다 --------------------------


@pytest.mark.parametrize("title", ["", "   "])
def test_service_rejects_empty_title(service, title):
    with pytest.raises(ValueError):
        service.add(title)
    assert service.list() == []


def test_service_strips_title(service):
    assert service.add("  산책  ").title == "산책"


def test_service_rejects_due_in_the_past(service):
    with pytest.raises(ValueError):
        service.add("늦은 일", due=date(2026, 2, 28))  # 가짜 시계의 오늘은 3월 1일
    assert service.list() == []


def test_service_accepts_due_today(service):
    assert service.add("오늘 일", due=date(2026, 3, 1)).due == date(2026, 3, 1)


def test_service_complete_twice_raises_already_done(service):
    service.add("a")
    service.complete(1)
    with pytest.raises(AlreadyDoneError):
        service.complete(1)


def test_service_complete_missing_raises_not_found(service):
    with pytest.raises(TaskNotFoundError):
        service.complete(42)


def test_service_list_filters_by_done(service):
    service.add("a")
    service.add("b")
    service.complete(1)
    assert [t.id for t in service.list()] == [1, 2]
    assert [t.id for t in service.list(done=False)] == [2]
    assert [t.id for t in service.list(done=True)] == [1]


def test_service_overdue_uses_injected_clock(service):
    service.add("어제까지", due=date(2026, 3, 1))
    service.add("다음 주", due=date(2026, 3, 8))
    service.add("마감 없음")
    assert service.overdue() == []
    later = TaskService(service.repo, clock=lambda: datetime(2026, 3, 5))
    assert [t.title for t in later.overdue()] == ["어제까지"]


# --- 테스트 대역(test double): Protocol 덕분에 어떤 객체든 꽂을 수 있다 -------


class RecordingFakeRepository:
    """호출 순서를 기록하는 가짜(fake). 실제로 동작하되 메모리에만 저장한다."""

    def __init__(self):
        self.calls: list[str] = []
        self._inner = MemoryTaskRepository()

    def __getattr__(self, name):
        method = getattr(self._inner, name)

        def recorder(*args, **kwargs):
            self.calls.append(name)
            return method(*args, **kwargs)

        return recorder


def test_service_checks_before_completing():
    """서비스는 complete 전에 반드시 get 으로 현재 상태를 확인해야 한다."""
    fake = RecordingFakeRepository()
    service = TaskService(fake, clock=fixed_clock)
    service.add("a")
    service.complete(1)
    assert fake.calls == ["add", "get", "complete"]
    assert isinstance(service.get(1), Task)
