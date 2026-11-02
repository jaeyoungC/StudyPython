"""02단원 테스트. 이 파일은 올바르며, 고치지 않습니다.

과제 4: 다섯 가지 pytest 기능(assert, raises, parametrize, tmp_path, monkeypatch)이
각각 어디에 쓰였는지 찾아 주석을 달아 보세요.
"""

import pytest

import buggy
from buggy import average, count_words, greeting, parse_age


# --- average ---------------------------------------------------------------

def test_average_of_numbers():
    assert average([1, 2, 3, 4]) == 2.5


def test_average_of_empty_list_raises():
    with pytest.raises(ValueError):
        average([])


# --- parse_age -------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [("30", 30), ("  30 ", 30), ("0", 0), ("150", 150)])
def test_parse_age_accepts_valid(text, expected):
    assert parse_age(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "-1", "151", "3.5"])
def test_parse_age_rejects_invalid(text):
    with pytest.raises(ValueError):
        parse_age(text)


# --- count_words -----------------------------------------------------------

def test_count_words_simple(tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("하나 둘 셋\n넷 다섯\n", encoding="utf-8")
    assert count_words(path) == 5


def test_count_words_ignores_extra_whitespace(tmp_path):
    path = tmp_path / "b.txt"
    path.write_text("하나   둘\n\n셋\n", encoding="utf-8")
    assert count_words(path) == 3


def test_count_words_empty_file(tmp_path):
    path = tmp_path / "c.txt"
    path.write_text("", encoding="utf-8")
    assert count_words(path) == 0


# --- greeting --------------------------------------------------------------

def test_greeting_morning():
    assert greeting("지영", now=lambda: 9) == "좋은 아침, 지영"


def test_greeting_afternoon():
    assert greeting("지영", now=lambda: 15) == "안녕하세요, 지영"


def test_greeting_with_monkeypatched_module_clock(monkeypatch):
    """모듈에 시계 함수가 있다고 가정하고 바꿔치기하는 예.

    buggy 모듈에는 current_hour가 없으므로 raising=False로 '없으면 만들어라'고 합니다.
    실제 프로젝트에서는 모듈이 가진 시계 함수를 이렇게 바꿉니다.
    """
    monkeypatch.setattr(buggy, "current_hour", lambda: 11, raising=False)
    assert greeting("지영", now=buggy.current_hour) == "좋은 아침, 지영"
