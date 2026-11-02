"""04단원 테스트. 실행: pytest units/04-classes"""

import pytest

from todo_classes import Task, TaskList, TaskNotFoundError


# --- Task ------------------------------------------------------------------

def test_task_stores_attributes():
    task = Task(1, "산책")
    assert task.id == 1
    assert task.title == "산책"
    assert task.done is False


def test_task_strips_title():
    assert Task(1, "  산책 ").title == "산책"


@pytest.mark.parametrize("title", ["", "   "])
def test_task_rejects_empty_title(title):
    with pytest.raises(ValueError):
        Task(1, title)


def test_task_complete():
    task = Task(1, "a")
    task.complete()
    assert task.done is True


def test_task_complete_twice_raises():
    task = Task(1, "a")
    task.complete()
    with pytest.raises(ValueError):
        task.complete()


# --- TaskList --------------------------------------------------------------

def test_add_assigns_increasing_ids():
    tasks = TaskList()
    assert tasks.add("a").id == 1
    assert tasks.add("b").id == 2
    assert tasks.count() == 2


def test_add_rejects_empty_title_and_keeps_list_unchanged():
    tasks = TaskList()
    with pytest.raises(ValueError):
        tasks.add("  ")
    assert tasks.count() == 0


def test_id_is_max_plus_one_after_remove():
    tasks = TaskList()
    tasks.add("a")
    tasks.add("b")
    tasks.remove(1)
    assert tasks.add("c").id == 3


def test_get_returns_same_object():
    tasks = TaskList()
    a = tasks.add("a")
    assert tasks.get(1) is a


def test_get_missing_raises_task_not_found():
    with pytest.raises(TaskNotFoundError):
        TaskList().get(1)


def test_task_not_found_is_a_value_error():
    # 03단원 CLI의 except ValueError 가 그대로 동작하는 이유
    with pytest.raises(ValueError):
        TaskList().get(1)


def test_complete_and_open_tasks():
    tasks = TaskList()
    tasks.add("a")
    tasks.add("b")
    assert tasks.complete(1).done is True
    assert [t.id for t in tasks.open_tasks()] == [2]


def test_all_returns_copy():
    tasks = TaskList()
    tasks.add("a")
    tasks.all().clear()          # 돌려받은 리스트를 비워도
    assert tasks.count() == 1    # 원본은 그대로여야 한다


def test_remove_missing_raises():
    with pytest.raises(TaskNotFoundError):
        TaskList().remove(1)
