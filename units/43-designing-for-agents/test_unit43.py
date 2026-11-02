"""43단원 테스트 뼈대. 실행: pytest units/43-designing-for-agents

각 테스트는 이름과 docstring 만 있고 본문은 `pytest.fail("아직 구현하지 않음")` 입니다.
mcp_tools.py 의 TODO 를 채우면서 각 본문을 실제 검증으로 바꾸세요.
서버(build_server)는 테스트하지 않습니다. 순수 함수만 봅니다.
"""

import pytest

from mcp_tools import (  # noqa: F401  (뼈대 단계에서는 아직 쓰지 않는 이름이 있습니다)
    MAX_LIMIT,
    _InMemoryRepo,
    add_task,
    complete_task,
    list_tasks,
    tool_descriptions,
)


@pytest.fixture
def repo():
    """빈 메모리 저장소. 실제 프로젝트에서는 SqliteTaskRepository(:memory:) 로 바꿉니다."""
    return _InMemoryRepo()


def test_list_returns_public_fields_only(repo):
    """list_tasks 의 각 항목은 id·title·done·due 네 필드만 가져야 한다 (창 절약)."""
    pytest.fail("아직 구현하지 않음")


def test_list_filters_by_done(repo):
    """done=False 면 미완료만, done=True 면 완료만, None 이면 전체를 돌려준다."""
    pytest.fail("아직 구현하지 않음")


def test_list_clamps_limit_to_max(repo):
    """limit=1000 을 주어도 MAX_LIMIT 개까지만 돌려주고, 0 이하는 1로 취급한다."""
    pytest.fail("아직 구현하지 않음")


def test_list_cursor_continues_without_overlap(repo):
    """next_cursor 로 다음 페이지를 받으면 앞 페이지와 겹치지 않고, 마지막 페이지의 next_cursor 는 None 이다."""
    pytest.fail("아직 구현하지 않음")


def test_add_returns_error_result_for_empty_title(repo):
    """빈 제목은 예외가 아니라 {"ok": False, "error": {"code": "invalid_title"}} 결과로 돌려준다."""
    pytest.fail("아직 구현하지 않음")


def test_add_with_same_idempotency_key_does_not_duplicate(repo):
    """같은 idempotency_key 로 두 번 부르면 같은 결과가 돌아오고 repo 에는 1건만 있다."""
    pytest.fail("아직 구현하지 않음")


def test_complete_missing_task_returns_not_found(repo):
    """없는 id 는 code "not_found" 오류 결과를 돌려준다."""
    pytest.fail("아직 구현하지 않음")


def test_complete_twice_returns_already_done(repo):
    """이미 완료된 할 일을 다시 완료하면 code "already_done" 오류 결과를 돌려준다 (409 와 같은 의미)."""
    pytest.fail("아직 구현하지 않음")


def test_tool_descriptions_are_short():
    """세 도구의 설명이 모두 있고, 길이 합이 400자 이하여야 한다 (설명은 모델의 창에 들어간다)."""
    pytest.fail("아직 구현하지 않음")
