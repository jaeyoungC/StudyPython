"""06단원 테스트. 실행: pytest units/06-package-and-cli

capsys: 테스트 동안 print 된 표준 출력(out)과 표준 오류(err)를 읽는 pytest 기능.
"""

import pytest

from todo.cli import format_task, main
from todo.models import Task, TaskList


def test_format_task_open_and_done():
    assert format_task(Task(1, "산책")) == "[ ] #1 산책"
    assert format_task(Task(2, "독서", done=True)) == "[x] #2 독서"


def test_add_prints_and_returns_zero(capsys):
    tasks = TaskList()
    code = main(["add", "산책"], tasks)
    assert code == 0
    assert capsys.readouterr().out.strip() == "추가: #1 산책"
    assert tasks.get(1).title == "산책"


def test_add_accepts_multiple_words(capsys):
    tasks = TaskList()
    assert main(["add", "SQL", "공부"], tasks) == 0
    assert tasks.get(1).title == "SQL 공부"


def test_add_empty_title_is_user_error(capsys):
    tasks = TaskList()
    code = main(["add", "   "], tasks)
    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert captured.err.startswith("오류:")
    assert len(tasks) == 0


def test_done_and_rm(capsys):
    tasks = TaskList()
    tasks.add("a")
    tasks.add("b")
    assert main(["done", "1"], tasks) == 0
    assert capsys.readouterr().out.strip() == "완료: #1 a"
    assert main(["rm", "2"], tasks) == 0
    assert capsys.readouterr().out.strip() == "삭제: #2 b"
    assert [t.id for t in tasks.all()] == [1]


def test_done_missing_id_is_user_error(capsys):
    code = main(["done", "99"], TaskList())
    assert code == 1
    assert "99" in capsys.readouterr().err


def test_ls_and_ls_open(capsys):
    tasks = TaskList()
    tasks.add("a")
    tasks.add("b")
    tasks.complete(1)
    assert main(["ls"], tasks) == 0
    assert capsys.readouterr().out.splitlines() == ["[x] #1 a", "[ ] #2 b"]
    assert main(["ls", "--open"], tasks) == 0
    assert capsys.readouterr().out.splitlines() == ["[ ] #2 b"]


def test_unknown_command_exits_with_argparse_code():
    with pytest.raises(SystemExit) as info:
        main(["fly"], TaskList())
    assert info.value.code == 2


def test_shell_runs_commands_until_quit(capsys, monkeypatch):
    lines = iter(['add "SQL 공부"', "done 1", "nonsense", "ls", "quit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(lines))
    tasks = TaskList()
    assert main(["shell"], tasks) == 0
    out = capsys.readouterr().out
    assert "추가: #1 SQL 공부" in out
    assert "[x] #1 SQL 공부" in out
    assert tasks.get(1).done is True
