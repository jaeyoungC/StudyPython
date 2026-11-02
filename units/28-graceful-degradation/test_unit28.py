"""28단원 테스트 뼈대. 실행: pytest units/28-graceful-degradation

각 테스트의 본문을 채우세요. 시계는 FakeClock 으로 주입하고, 실제로 기다리는 테스트는 없어야 합니다.
pytest.fail("아직 구현하지 않음") 을 지우고 그 자리에 준비(arrange) → 실행(act) → 단언(assert) 을 씁니다.
"""

import pytest

from circuit import Bulkhead, BulkheadFullError, CircuitBreaker, CircuitOpenError, CircuitState, with_fallback


class FakeClock:
    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class FailingThenWorking:
    """처음 fail_times 번은 error 를 던지고, 그 뒤로는 "ok" 를 돌려준다. 호출 횟수를 센다."""

    def __init__(self, fail_times: int, error: BaseException = ConnectionError("notifier down")) -> None:
        self.fail_times = fail_times
        self.error = error
        self.calls = 0

    def __call__(self) -> str:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise self.error
        return "ok"


# ---------------------------------------------------------------------------
# 서킷 브레이커 상태 기계
# ---------------------------------------------------------------------------


def test_starts_closed_and_passes_calls_through():
    """새 브레이커는 CLOSED 이고 fn 의 결과를 그대로 돌려준다."""
    pytest.fail("아직 구현하지 않음")


def test_opens_after_threshold_consecutive_failures():
    """failure_threshold=3 에서 연속 3번 실패하면 state 가 OPEN 이 된다. 2번째까지는 CLOSED."""
    pytest.fail("아직 구현하지 않음")


def test_open_circuit_rejects_without_calling():
    """OPEN 상태에서 call 은 fn 을 부르지 않고 CircuitOpenError 를 던진다 (fn.calls 가 늘지 않는다)."""
    pytest.fail("아직 구현하지 않음")


def test_success_resets_consecutive_failure_count():
    """실패 2번 → 성공 1번 → 실패 2번 이면 아직 CLOSED (연속이 아니므로)."""
    pytest.fail("아직 구현하지 않음")


def test_moves_to_half_open_after_recovery_timeout():
    """OPEN 뒤 clock 을 recovery_timeout 만큼 넘기면 state 가 HALF_OPEN."""
    pytest.fail("아직 구현하지 않음")


def test_half_open_success_closes_circuit():
    """HALF_OPEN 에서 시험 호출이 성공하면 CLOSED 가 되고 다음 호출도 통과한다."""
    pytest.fail("아직 구현하지 않음")


def test_half_open_failure_reopens_circuit():
    """HALF_OPEN 에서 시험 호출이 실패하면 다시 OPEN 이고, recovery_timeout 이 새로 시작된다."""
    pytest.fail("아직 구현하지 않음")


def test_non_failure_exceptions_pass_through_and_do_not_count():
    """ValueError 는 failure_on 에 없으므로 그대로 전파되고 실패 횟수에 들어가지 않는다."""
    pytest.fail("아직 구현하지 않음")


def test_invalid_arguments_are_rejected():
    """failure_threshold < 1 또는 recovery_timeout <= 0 이면 ValueError."""
    pytest.fail("아직 구현하지 않음")


# ---------------------------------------------------------------------------
# 폴백
# ---------------------------------------------------------------------------


def test_with_fallback_returns_primary_result_when_it_works():
    """fn 이 성공하면 fallback 은 불리지 않는다."""
    pytest.fail("아직 구현하지 않음")


def test_with_fallback_uses_fallback_on_listed_errors():
    """fn 이 CircuitOpenError 를 던지면 fallback(예외) 의 결과를 돌려준다. fallback 은 받은 예외가 그 예외인지 확인한다."""
    pytest.fail("아직 구현하지 않음")


def test_with_fallback_lets_other_errors_through():
    """on=(CircuitOpenError,) 인데 fn 이 KeyError 를 던지면 KeyError 가 그대로 전파된다."""
    pytest.fail("아직 구현하지 않음")


# ---------------------------------------------------------------------------
# 격벽
# ---------------------------------------------------------------------------


def test_bulkhead_allows_up_to_max_concurrent():
    """max_concurrent=2 이면 slot() 두 개를 동시에 열 수 있고 available 은 0 이 된다."""
    pytest.fail("아직 구현하지 않음")


def test_bulkhead_rejects_when_full():
    """자리가 없을 때 slot() 은 기다리지 않고 BulkheadFullError 를 던진다."""
    pytest.fail("아직 구현하지 않음")


def test_bulkhead_releases_slot_even_when_block_raises():
    """with 블록 안에서 예외가 나도 available 이 원래대로 돌아온다."""
    pytest.fail("아직 구현하지 않음")


# ---------------------------------------------------------------------------
# 합치기: 브레이커 + 폴백 = "외부 API가 멈추면 사용자는 무엇을 보는가"
# ---------------------------------------------------------------------------


def test_degraded_completion_still_succeeds_without_notifier():
    """notifier 가 죽어 서킷이 열려도, 할 일 완료(핵심 기능)는 성공하고 알림은 '나중에 보냄' 큐에 쌓인다.

    브레이커.call(알림) 을 with_fallback 으로 감싸 폴백이 큐 리스트에 append 하도록 만들고,
    완료 결과와 큐 길이를 단언한다.
    """
    pytest.fail("아직 구현하지 않음")
