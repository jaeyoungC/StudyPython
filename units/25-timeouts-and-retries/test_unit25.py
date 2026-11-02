"""25단원 테스트. 실행: pytest units/25-timeouts-and-retries

시간과 난수는 모두 주입합니다. 테스트 안에서 time.sleep 을 진짜로 부르는 곳은 없습니다.
call_with_timeout 테스트만 0.02초짜리 실제 대기를 합니다(타임아웃은 진짜 시간 없이는 검증할 수 없습니다).
"""

import random
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from retry import TRANSIENT_ERRORS, RetryError, backoff_delay, call_with_timeout, retry


# ---------------------------------------------------------------------------
# 주입용 대역
# ---------------------------------------------------------------------------


class FakeSleep:
    """잠들지 않고 요청받은 시간만 기록한다."""

    def __init__(self) -> None:
        self.calls: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.calls.append(seconds)


class MaxRng:
    """uniform(a, b) 가 항상 b 를 돌려준다 → 지터가 없는 '최악의 대기'를 결정적으로 본다."""

    def uniform(self, a: float, b: float) -> float:
        return b


class FlakyFn:
    """처음 fail_times 번은 error 를 던지고 그다음부터 value 를 돌려준다."""

    def __init__(self, fail_times: int, error: BaseException, value="ok") -> None:
        self.fail_times = fail_times
        self.error = error
        self.value = value
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise self.error
        return self.value


# ---------------------------------------------------------------------------
# backoff_delay
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("attempt, expected", [(0, 1.0), (1, 2.0), (2, 4.0), (3, 8.0)])
def test_backoff_doubles_each_attempt(attempt, expected):
    assert backoff_delay(attempt, base_delay=1.0, max_delay=100.0, rng=MaxRng()) == expected


def test_backoff_is_capped_by_max_delay():
    assert backoff_delay(10, base_delay=1.0, max_delay=5.0, rng=MaxRng()) == 5.0


def test_backoff_jitter_stays_within_range():
    rng = random.Random(0)  # 시드를 고정하면 "난수"도 재현된다
    samples = [backoff_delay(3, base_delay=1.0, max_delay=100.0, rng=rng) for _ in range(200)]
    assert all(0.0 <= s <= 8.0 for s in samples)
    assert len(set(round(s, 6) for s in samples)) > 100  # 정말 흩어져 있다


def test_backoff_rejects_negative_attempt():
    with pytest.raises(ValueError):
        backoff_delay(-1, base_delay=1.0, max_delay=1.0, rng=MaxRng())


# ---------------------------------------------------------------------------
# retry
# ---------------------------------------------------------------------------


def test_success_on_first_try_does_not_sleep():
    sleep = FakeSleep()
    assert retry(lambda: 42, attempts=3, sleep=sleep, rng=MaxRng()) == 42
    assert sleep.calls == []


def test_retries_transient_error_then_succeeds():
    fn = FlakyFn(fail_times=2, error=ConnectionError("down"))
    sleep = FakeSleep()
    assert retry(fn, attempts=3, base_delay=1.0, max_delay=10.0, sleep=sleep, rng=MaxRng()) == "ok"
    assert fn.calls == 3
    assert sleep.calls == [1.0, 2.0]  # 시도 사이에만, 지수적으로


def test_gives_up_after_attempts_with_retry_error():
    fn = FlakyFn(fail_times=99, error=TimeoutError("slow"))
    sleep = FakeSleep()
    with pytest.raises(RetryError) as info:
        retry(fn, attempts=3, base_delay=1.0, max_delay=10.0, sleep=sleep, rng=MaxRng())
    assert fn.calls == 3
    assert info.value.attempts == 3
    assert isinstance(info.value.last_exception, TimeoutError)
    assert isinstance(info.value.__cause__, TimeoutError)  # raise ... from
    assert sleep.calls == [1.0, 2.0]  # 마지막 실패 뒤에는 자지 않는다


def test_non_retryable_error_is_raised_immediately():
    fn = FlakyFn(fail_times=99, error=ValueError("내 잘못"))
    sleep = FakeSleep()
    with pytest.raises(ValueError):
        retry(fn, attempts=5, sleep=sleep, rng=MaxRng())
    assert fn.calls == 1
    assert sleep.calls == []


def test_retry_on_is_configurable():
    fn = FlakyFn(fail_times=1, error=KeyError("cache miss"))
    sleep = FakeSleep()
    assert retry(fn, attempts=2, retry_on=(KeyError,), sleep=sleep, rng=MaxRng()) == "ok"
    assert fn.calls == 2


def test_attempts_one_means_no_retry():
    fn = FlakyFn(fail_times=1, error=ConnectionError())
    sleep = FakeSleep()
    with pytest.raises(RetryError):
        retry(fn, attempts=1, sleep=sleep, rng=MaxRng())
    assert fn.calls == 1
    assert sleep.calls == []


def test_attempts_below_one_is_rejected_before_calling():
    fn = FlakyFn(fail_times=0, error=None)
    with pytest.raises(ValueError):
        retry(fn, attempts=0, sleep=FakeSleep(), rng=MaxRng())
    assert fn.calls == 0


def test_delays_respect_max_delay():
    fn = FlakyFn(fail_times=4, error=ConnectionError())
    sleep = FakeSleep()
    retry(fn, attempts=5, base_delay=1.0, max_delay=3.0, sleep=sleep, rng=MaxRng())
    assert sleep.calls == [1.0, 2.0, 3.0, 3.0]


def test_default_transient_errors_do_not_include_value_error():
    assert TimeoutError in TRANSIENT_ERRORS
    assert ConnectionError in TRANSIENT_ERRORS
    assert ValueError not in TRANSIENT_ERRORS


def test_subclass_of_retryable_error_is_retried():
    fn = FlakyFn(fail_times=1, error=ConnectionRefusedError())  # ConnectionError 의 하위 클래스
    assert retry(fn, attempts=2, sleep=FakeSleep(), rng=MaxRng()) == "ok"


# ---------------------------------------------------------------------------
# call_with_timeout
# ---------------------------------------------------------------------------


def test_fast_function_returns_its_value():
    assert call_with_timeout(lambda: "fast", seconds=1.0) == "fast"


def test_slow_function_raises_timeout_error():
    release = threading.Event()  # 테스트 끝에 풀어 줘서 스레드가 남지 않게 한다
    executor = ThreadPoolExecutor(max_workers=1)
    try:
        with pytest.raises(TimeoutError):
            call_with_timeout(release.wait, seconds=0.02, executor=executor)
    finally:
        release.set()
        executor.shutdown(wait=True)


def test_exception_inside_function_propagates():
    def boom():
        raise KeyError("x")

    with pytest.raises(KeyError):
        call_with_timeout(boom, seconds=1.0)


def test_timeout_and_retry_compose():
    """타임아웃은 TimeoutError 를 던지고, retry 는 그것을 일시적 오류로 보고 재시도한다."""
    fn = FlakyFn(fail_times=1, error=TimeoutError("첫 호출은 느렸다"))
    sleep = FakeSleep()
    assert retry(lambda: call_with_timeout(fn, seconds=1.0), attempts=2, sleep=sleep, rng=MaxRng()) == "ok"
    assert fn.calls == 2
    assert len(sleep.calls) == 1
