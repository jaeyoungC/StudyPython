import pytest

from task_model import Task, TaskList, TaskNotFoundError


def test_task_strips_title():
    assert Task(id=1, title="  산책 ").title == "산책"


@pytest.mark.parametrize("title", ["", "   "])
def test_task_rejects_empty_title(title):
    with pytest.raises(ValueError):
        Task(id=1, title=title)


def test_task_complete():
    task = Task(id=1, title="a")
    task.complete()
    assert task.done is True


def test_task_complete_twice_raises():
    task = Task(id=1, title="a")
    task.complete()
    with pytest.raises(ValueError):
        task.complete()


def test_tasklist_add_assigns_ids():
    tasks = TaskList()
    assert tasks.add("a").id == 1
    assert tasks.add("b").id == 2
    assert len(tasks) == 2


def test_tasklist_add_rejects_empty_title():
    tasks = TaskList()
    with pytest.raises(ValueError):
        tasks.add("  ")
    assert len(tasks) == 0


def test_tasklist_id_after_remove():
    tasks = TaskList()
    tasks.add("a")
    tasks.add("b")
    tasks.remove(1)
    assert tasks.add("c").id == 3


def test_tasklist_get_missing_raises_specific_error():
    tasks = TaskList()
    with pytest.raises(TaskNotFoundError):
        tasks.get(1)


def test_task_not_found_is_value_error():
    assert issubclass(TaskNotFoundError, ValueError)


def test_tasklist_complete_and_open_tasks():
    tasks = TaskList()
    tasks.add("a")
    tasks.add("b")
    assert tasks.complete(1).done is True
    assert [t.id for t in tasks.open_tasks()] == [2]


def test_open_tasks_returns_copy():
    tasks = TaskList()
    tasks.add("a")
    tasks.open_tasks().clear()
    assert len(tasks) == 1


def test_tasklist_remove_missing_raises():
    with pytest.raises(TaskNotFoundError):
        TaskList().remove(1)
