"""03단원 테스트. 실행: pytest units/03-functions

테스트 함수 이름은 "무엇을 하면 무엇이 되어야 한다"를 읽히게 짓습니다.
"""

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


# parametrize: 같은 테스트를 여러 입력으로 반복합니다 (02단원).
@pytest.mark.parametrize("title", ["", "   "])
def test_add_rejects_empty_title(title):
    tasks = []
    with pytest.raises(ValueError):
        add_task(tasks, title)
    assert tasks == []  # 실패한 추가는 목록을 바꾸면 안 된다


def test_id_is_max_plus_one_after_remove():
    tasks = []
    add_task(tasks, "a")
    add_task(tasks, "b")
    remove_task(tasks, 1)
    # len(tasks) + 1 이면 2가 되어 기존 id와 겹친다
    assert add_task(tasks, "c")["id"] == 3


def test_find_task_returns_the_same_object():
    tasks = []
    add_task(tasks, "a")
    b = add_task(tasks, "b")
    # `is`: 값이 같은 복사본이 아니라 같은 객체여야 한다
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


def test_list_tasks_filters_open():
    tasks = []
    add_task(tasks, "a")
    add_task(tasks, "b")
    complete_task(tasks, 1)
    assert [t["id"] for t in list_tasks(tasks, only_open=True)] == [2]


def test_list_tasks_returns_new_list():
    tasks = []
    add_task(tasks, "a")
    result = list_tasks(tasks)
    assert result == tasks
    assert result is not tasks  # 새 리스트여야 호출한 쪽이 지워도 원본이 안전하다
