import pytest

from todo_memory import add_task, complete_task, find_task, list_tasks, remove_task


def test_add_first_task_gets_id_1():
    tasks = []
    task = add_task(tasks, "SQL 공부")
    assert task == {"id": 1, "title": "SQL 공부", "done": False}
    assert tasks == [task]


def test_add_strips_whitespace():
    tasks = []
    assert add_task(tasks, "  산책  ")["title"] == "산책"


@pytest.mark.parametrize("title", ["", "   "])
def test_add_rejects_empty_title(title):
    tasks = []
    with pytest.raises(ValueError):
        add_task(tasks, title)
    assert tasks == []


def test_id_is_max_plus_one_after_remove():
    tasks = []
    add_task(tasks, "a")
    add_task(tasks, "b")
    remove_task(tasks, 1)
    # len(tasks) + 1 이면 2가 되어 기존 id와 겹친다
    assert add_task(tasks, "c")["id"] == 3


def test_find_task():
    tasks = []
    add_task(tasks, "a")
    b = add_task(tasks, "b")
    assert find_task(tasks, 2) is b


def test_find_missing_task_raises():
    with pytest.raises(ValueError):
        find_task([], 1)


def test_complete_task():
    tasks = []
    add_task(tasks, "a")
    assert complete_task(tasks, 1)["done"] is True
    assert tasks[0]["done"] is True


def test_complete_missing_task_raises():
    with pytest.raises(ValueError):
        complete_task([], 99)


def test_remove_task_returns_removed():
    tasks = []
    add_task(tasks, "a")
    add_task(tasks, "b")
    removed = remove_task(tasks, 1)
    assert removed["title"] == "a"
    assert [t["id"] for t in tasks] == [2]


def test_remove_missing_task_raises():
    with pytest.raises(ValueError):
        remove_task([], 1)


def test_list_tasks_filters_open_and_returns_new_list():
    tasks = []
    add_task(tasks, "a")
    add_task(tasks, "b")
    complete_task(tasks, 1)

    open_tasks = list_tasks(tasks, only_open=True)
    assert [t["id"] for t in open_tasks] == [2]

    all_tasks = list_tasks(tasks)
    assert len(all_tasks) == 2
    assert all_tasks is not tasks
