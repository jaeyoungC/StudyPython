"""05단원 테스트. 실행: pytest units/05-dataclasses"""

import pytest

from todo_dataclass import Task, TaskList, TaskNotFoundError


# --- Task ------------------------------------------------------------------

def test_task_strips_and_defaults():
    task = Task(1, "  산책 ")
    assert (task.id, task.title, task.done) == (1, "산책", False)


@pytest.mark.parametrize("title", ["", "   "])
def test_task_rejects_empty_title(title):
    with pytest.raises(ValueError):
        Task(1, title)


def test_dataclass_gives_equality_and_repr():
    assert Task(1, "a") == Task(1, "a")
    assert "산책" in repr(Task(2, "산책"))


def test_complete_twice_raises():
    task = Task(1, "a")
    task.complete()
    with pytest.raises(ValueError):
        task.complete()


def test_to_dict():
    assert Task(1, "산책", True).to_dict() == {"id": 1, "title": "산책", "done": True}


def test_from_dict_roundtrip():
    original = Task(3, "SQL 공부")
    assert Task.from_dict(original.to_dict()) == original


def test_from_dict_done_defaults_to_false():
    assert Task.from_dict({"id": 1, "title": "a"}).done is False


@pytest.mark.parametrize(
    "data",
    [
        {"title": "a"},                       # id 없음
        {"id": 1},                            # title 없음
        {"id": "1", "title": "a"},            # id 가 문자열
        {"id": 1, "title": 5},                # title 이 숫자
        {"id": 1, "title": "a", "done": "y"}, # done 이 문자열
        {"id": 1, "title": "   "},            # 빈 제목
    ],
)
def test_from_dict_rejects_bad_data(data):
    with pytest.raises(ValueError):
        Task.from_dict(data)


# --- TaskList --------------------------------------------------------------

def test_add_and_len():
    tasks = TaskList()
    tasks.add("a")
    tasks.add("b")
    assert len(tasks) == 2


def test_two_lists_do_not_share_storage():
    # field(default_factory=list) 가 없으면 이 테스트가 깨진다
    a = TaskList()
    b = TaskList()
    a.add("x")
    assert len(b) == 0


def test_get_same_object_and_missing():
    tasks = TaskList()
    t = tasks.add("a")
    assert tasks.get(1) is t
    with pytest.raises(TaskNotFoundError):
        tasks.get(2)


def test_find_by_title_returns_task_or_none():
    tasks = TaskList()
    t = tasks.add("산책")
    assert tasks.find("산책") is t
    assert tasks.find("없음") is None


def test_iteration_yields_tasks_in_order():
    tasks = TaskList()
    tasks.add("a")
    tasks.add("b")
    assert [t.title for t in tasks] == ["a", "b"]


def test_complete_remove_open_all():
    tasks = TaskList()
    tasks.add("a")
    tasks.add("b")
    tasks.add("c")
    tasks.complete(1)
    tasks.remove(2)
    assert [t.id for t in tasks.open_tasks()] == [3]
    assert [t.id for t in tasks.all()] == [1, 3]
    assert tasks.all() is not tasks._tasks
