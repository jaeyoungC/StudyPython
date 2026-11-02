import json

import pytest

from json_store import StoreError, load_tasks, save_tasks

TASKS = [
    {"id": 1, "title": "SQL 공부", "done": False},
    {"id": 2, "title": "산책", "done": True},
]


def test_load_missing_file_returns_empty(tmp_path):
    assert load_tasks(tmp_path / "tasks.json") == []


def test_save_then_load_roundtrip(tmp_path):
    path = tmp_path / "tasks.json"
    save_tasks(path, TASKS)
    assert load_tasks(path) == TASKS


def test_save_keeps_korean_readable(tmp_path):
    path = tmp_path / "tasks.json"
    save_tasks(path, TASKS)
    assert "SQL 공부" in path.read_text(encoding="utf-8")


def test_save_overwrites_previous(tmp_path):
    path = tmp_path / "tasks.json"
    save_tasks(path, TASKS)
    save_tasks(path, TASKS[:1])
    assert load_tasks(path) == TASKS[:1]


def test_save_leaves_no_temp_file(tmp_path):
    path = tmp_path / "tasks.json"
    save_tasks(path, TASKS)
    assert [p.name for p in tmp_path.iterdir()] == ["tasks.json"]


def test_save_uses_os_replace(tmp_path, monkeypatch):
    """원자적 쓰기를 했는지 확인: os.replace가 호출되어야 한다."""
    import json_store

    calls = []
    real_replace = json_store.os.replace

    def spy(src, dst):
        calls.append((str(src), str(dst)))
        real_replace(src, dst)

    monkeypatch.setattr(json_store.os, "replace", spy)
    path = tmp_path / "tasks.json"
    save_tasks(path, TASKS)
    assert len(calls) == 1
    assert calls[0][1] == str(path)


def test_load_corrupted_file_raises_store_error(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text("{ 깨진 json", encoding="utf-8")
    with pytest.raises(StoreError) as info:
        load_tasks(path)
    assert isinstance(info.value.__cause__, json.JSONDecodeError)


def test_load_non_list_raises_store_error(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text('{"id": 1}', encoding="utf-8")
    with pytest.raises(StoreError):
        load_tasks(path)
