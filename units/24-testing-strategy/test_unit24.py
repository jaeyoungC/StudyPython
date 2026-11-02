"""24단원 테스트. 실행: pytest units/24-testing-strategy

세 가지 테스트 대역(test double)을 나란히 둡니다.
- 가짜(fake):  진짜처럼 "동작"하는 단순 구현. 보낸 것을 메모리에 쌓아 둔다.
- 스텁(stub):  정해진 답만 돌려준다. "항상 실패"처럼 특정 상황을 만들 때 쓴다.
- 목(mock):    "어떻게 호출되었는가"를 기록하고 검증한다(unittest.mock.Mock).

README의 "테스트가 내 목표를 반영하는가" 절과 함께 읽으세요. 이 파일에는 일부러 약하게 쓴 테스트가
하나 있고(이름에 FIX_ME), 그것을 고치는 것이 과제의 일부입니다.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from completion_notifier import (
    FileSender,
    NotifyResult,
    Sender,
    build_message,
    notify_completed,
    summarize,
)

NOW = datetime(2026, 11, 2, 9, 30)


def fixed_clock() -> datetime:
    return NOW


# ---------------------------------------------------------------------------
# 1. 단위 테스트(unit test): 의존성이 없는 순수 함수는 대역이 필요 없다.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tasks, expected",
    [
        ([], {"total": 0, "done": 0, "open": 0, "done_ratio": 0.0}),
        (
            [{"id": 1, "title": "a", "done": True}, {"id": 2, "title": "b", "done": False}],
            {"total": 2, "done": 1, "open": 1, "done_ratio": 0.5},
        ),
        (
            [{"id": 1, "title": "a", "done": True}],
            {"total": 1, "done": 1, "open": 0, "done_ratio": 1.0},
        ),
    ],
)
def test_summarize_counts(tasks, expected):
    assert summarize(tasks) == expected


def test_summarize_does_not_mutate_input():
    tasks = [{"id": 1, "title": "a", "done": False}]
    before = [dict(t) for t in tasks]
    summarize(tasks)
    assert tasks == before


def test_build_message_format():
    task = {"id": 1, "title": "SQL 공부", "done": True}
    assert build_message(task, NOW) == "[2026-11-02 09:30] 할 일 완료: SQL 공부"


# ---------------------------------------------------------------------------
# 2. 가짜(fake): 진짜처럼 동작하지만 단순한 구현. 상태를 가진다.
# ---------------------------------------------------------------------------


class FakeSender:
    """보낸 알림을 메모리에 쌓는다. fail_for 에 든 주소로는 실패(False)한다."""

    def __init__(self, fail_for: set[str] | None = None) -> None:
        self.sent: list[tuple[str, str]] = []
        self.fail_for = fail_for or set()

    def send(self, to: str, message: str) -> bool:
        if to in self.fail_for:
            return False
        self.sent.append((to, message))
        return True


def test_fake_records_what_was_sent():
    sender = FakeSender()
    task = {"id": 1, "title": "SQL 공부", "done": True}

    result = notify_completed(task, "me@example.com", sender, clock=fixed_clock)

    assert result == NotifyResult(delivered=True, message="[2026-11-02 09:30] 할 일 완료: SQL 공부")
    assert sender.sent == [("me@example.com", "[2026-11-02 09:30] 할 일 완료: SQL 공부")]


def test_fake_can_simulate_failure_for_one_address():
    sender = FakeSender(fail_for={"down@example.com"})
    task = {"id": 1, "title": "a", "done": True}

    assert notify_completed(task, "down@example.com", sender, clock=fixed_clock).delivered is False
    assert notify_completed(task, "ok@example.com", sender, clock=fixed_clock).delivered is True
    assert [to for to, _ in sender.sent] == ["ok@example.com"]


# ---------------------------------------------------------------------------
# 3. 스텁(stub): 정해진 답만 돌려준다. 상태도, 검증도 없다.
# ---------------------------------------------------------------------------


class AlwaysFailingSender:
    def send(self, to: str, message: str) -> bool:
        return False


def test_stub_forces_the_failure_path():
    task = {"id": 1, "title": "a", "done": True}
    result = notify_completed(task, "me@example.com", AlwaysFailingSender(), clock=fixed_clock)
    assert result.delivered is False
    # 실패해도 본문은 만들어져 있어야 한다(재시도나 로그에 쓰기 위해)
    assert result.message.endswith("할 일 완료: a")


# ---------------------------------------------------------------------------
# 4. 목(mock): "어떻게 호출되었는가"를 검증한다. unittest.mock.Mock
# ---------------------------------------------------------------------------


def test_mock_verifies_exact_call():
    sender = Mock(spec=Sender)  # spec: Sender 에 없는 메서드를 부르면 AttributeError
    sender.send.return_value = True
    task = {"id": 7, "title": "산책", "done": True}

    notify_completed(task, "me@example.com", sender, clock=fixed_clock)

    sender.send.assert_called_once_with("me@example.com", "[2026-11-02 09:30] 할 일 완료: 산책")


def test_mock_proves_nothing_is_sent_for_open_task():
    sender = Mock(spec=Sender)
    task = {"id": 1, "title": "a", "done": False}

    with pytest.raises(ValueError):
        notify_completed(task, "me@example.com", sender, clock=fixed_clock)

    sender.send.assert_not_called()


def test_mock_proves_nothing_is_sent_for_bad_email():
    sender = Mock(spec=Sender)
    task = {"id": 1, "title": "a", "done": True}

    with pytest.raises(ValueError):
        notify_completed(task, "not-an-email", sender, clock=fixed_clock)

    sender.send.assert_not_called()


# ---------------------------------------------------------------------------
# 5. 일부러 약하게 쓴 테스트. 이대로도 통과하지만, 내 목표를 반영하지 않는다.
#
#    실험: completion_notifier.notify_completed 가 sender.send("", "") 를 부르도록 고의로 망가뜨린 뒤
#    pytest 를 돌려 보세요. 이 테스트는 여전히 통과합니다. 무엇을 확인해야 할지 정하고 고치세요.
#    고친 뒤에는 이름에서 __FIX_ME 를 떼세요.
# ---------------------------------------------------------------------------


def test_notify_sends_something__FIX_ME():
    sender = Mock(spec=Sender)
    sender.send.return_value = True
    task = {"id": 1, "title": "SQL 공부", "done": True}

    result = notify_completed(task, "me@example.com", sender, clock=fixed_clock)

    assert sender.send.called
    assert result.delivered


# ---------------------------------------------------------------------------
# 6. 계약 테스트(contract test): 가짜와 진짜 어댑터가 같은 약속을 지키는지 같은 테스트로 확인한다.
#    가짜가 진짜와 다르게 행동하면, 가짜로 통과한 테스트는 아무것도 보장하지 않는다.
# ---------------------------------------------------------------------------


@pytest.fixture(params=["fake", "file"])
def sender_and_reader(request, tmp_path):
    """(sender, 보낸 내용을 읽어 오는 함수) 쌍을 돌려준다."""
    if request.param == "fake":
        sender = FakeSender()
        return sender, lambda: list(sender.sent)
    path = tmp_path / "sent.log"
    sender = FileSender(path)

    def read_back() -> list[tuple[str, str]]:
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
        return [tuple(line.split("\t", 1)) for line in lines]

    return sender, read_back


def test_contract_send_returns_true_and_is_retrievable(sender_and_reader):
    sender, read_back = sender_and_reader
    assert sender.send("a@example.com", "hello") is True
    assert sender.send("b@example.com", "world") is True
    assert read_back() == [("a@example.com", "hello"), ("b@example.com", "world")]


def test_contract_nothing_sent_means_nothing_retrievable(sender_and_reader):
    _, read_back = sender_and_reader
    assert read_back() == []
