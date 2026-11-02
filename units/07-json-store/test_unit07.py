"""07단원 테스트. 실행: pytest units/07-json-store"""

import json

import pytest

from todo.cli import main
from todo.models import Task
from todo.storage_json import JsonTaskStore, StoreError

TASKS = [Task(1, "SQL 공부"), Task(2, "산책", done=True)]


# --- load ------------------------------------------------------------------

def test_load_missing_file_returns_empty(tmp_path):
    assert JsonTaskStore(tmp_path / "todo.json").load() == []


def test_save_then_load_roundtrip(tmp_path):
    store = JsonTaskStore(tmp_path / "todo.json")
    store.save(TASKS)
    assert store.load() == TASKS


def test_load_corrupted_json_raises_store_error_with_cause(tmp_path):
    path = tmp_path / "todo.json"
    path.write_text("{ 깨진", encoding="utf-8")
    with pytest.raises(StoreError) as info:
        JsonTaskStore(path).load()
    # `raise ... from error` 를 썼는지: 원인 예외가 연결되어 있어야 한다
    assert isinstance(info.value.__cause__, json.JSONDecodeError)


@pytest.mark.parametrize(
    "content",
    [
        '{"id": 1, "title": "a"}',           # 최상위가 리스트가 아님
        '[{"id": "1", "title": "a"}]',       # 항목이 Task.from_dict 를 통과하지 못함
        '[{"title": "a"}]',                  # id 없음
    ],
)
def test_load_invalid_structure_raises_store_error(tmp_path, content):
    path = tmp_path / "todo.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(StoreError):
        JsonTaskStore(path).load()


# --- save ------------------------------------------------------------------

def test_save_keeps_korean_readable(tmp_path):
    path = tmp_path / "todo.json"
    JsonTaskStore(path).save(TASKS)
    assert "SQL 공부" in path.read_text(encoding="utf-8")


def test_save_overwrites_previous(tmp_path):
    store = JsonTaskStore(tmp_path / "todo.json")
    store.save(TASKS)
    store.save(TASKS[:1])
    assert store.load() == TASKS[:1]


def test_save_leaves_only_the_target_file(tmp_path):
    JsonTaskStore(tmp_path / "todo.json").save(TASKS)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["todo.json"]


def test_failed_save_keeps_original_file_intact(tmp_path, monkeypatch):
    """원자적 쓰기의 핵심: 저장 도중 실패해도 원본은 그대로여야 한다."""
    path = tmp_path / "todo.json"
    store = JsonTaskStore(path)
    store.save(TASKS)
    before = path.read_text(encoding="utf-8")

    # 직렬화 단계에서 터지게 만든다 (어떤 구현이든 json.dumps 는 거친다)
    import todo.storage_json as storage_module

    def boom(*args, **kwargs):
        raise RuntimeError("디스크가 가득 찼다고 치자")

    monkeypatch.setattr(storage_module.json, "dumps", boom)
    with pytest.raises(RuntimeError):
        store.save(TASKS[:1])

    assert path.read_text(encoding="utf-8") == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["todo.json"]


# --- CLI 연결 ---------------------------------------------------------------

def test_cli_persists_between_runs(tmp_path, capsys):
    file = str(tmp_path / "todo.json")
    assert main(["--file", file, "add", "산책"]) == 0
    assert main(["--file", file, "add", "SQL", "공부"]) == 0
    assert main(["--file", file, "done", "1"]) == 0
    capsys.readouterr()
    assert main(["--file", file, "ls"]) == 0
    assert capsys.readouterr().out.splitlines() == ["[x] #1 산책", "[ ] #2 SQL 공부"]


def test_cli_does_not_save_on_user_error(tmp_path, capsys):
    file = tmp_path / "todo.json"
    assert main(["--file", str(file), "done", "7"]) == 1
    assert not file.exists()


def test_cli_reports_corrupted_file(tmp_path, capsys):
    file = tmp_path / "todo.json"
    file.write_text("{ 깨진", encoding="utf-8")
    assert main(["--file", str(file), "ls"]) == 1
    assert capsys.readouterr().err.startswith("오류:")


def test_cli_shell_saves_after_each_command(tmp_path, capsys, monkeypatch):
    file = tmp_path / "todo.json"
    lines = iter(["add 산책", "quit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(lines))
    assert main(["--file", str(file), "shell"]) == 0
    assert JsonTaskStore(file).load() == [Task(1, "산책")]
