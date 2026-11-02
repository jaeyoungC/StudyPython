"""27단원 테스트. 실행: pytest units/27-rate-limiting

시계는 FakeClock 으로 주입합니다. 테스트 어디에서도 실제로 기다리지 않습니다.
"""

import pytest

from ratelimit import RateLimiter, retry_after_header


class FakeClock:
    def __init__(self, now: float = 100.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock():
    return FakeClock()


# ---------------------------------------------------------------------------
# 생성과 검증
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rate, capacity", [(0, 5), (-1.0, 5), (1.0, 0), (1.0, -3)])
def test_invalid_arguments_are_rejected(rate, capacity, clock):
    with pytest.raises(ValueError):
        RateLimiter(rate, capacity, clock=clock)


def test_new_key_starts_with_full_bucket(clock):
    limiter = RateLimiter(rate=1.0, capacity=5, clock=clock)
    assert limiter.tokens("alice") == 5.0


# ---------------------------------------------------------------------------
# 버스트와 거절
# ---------------------------------------------------------------------------


def test_allows_capacity_requests_in_a_burst(clock):
    limiter = RateLimiter(rate=1.0, capacity=3, clock=clock)
    assert [limiter.allow("alice") for _ in range(3)] == [(True, 0.0)] * 3


def test_request_beyond_capacity_is_denied_with_retry_after(clock):
    limiter = RateLimiter(rate=1.0, capacity=3, clock=clock)
    for _ in range(3):
        limiter.allow("alice")

    allowed, retry_after = limiter.allow("alice")

    assert allowed is False
    assert retry_after == pytest.approx(1.0)  # 토큰 1개가 차는 데 1/rate 초


def test_denied_request_does_not_consume_tokens(clock):
    limiter = RateLimiter(rate=1.0, capacity=1, clock=clock)
    limiter.allow("alice")
    limiter.allow("alice")  # 거절
    limiter.allow("alice")  # 거절
    clock.advance(1.0)
    assert limiter.allow("alice") == (True, 0.0)  # 거절이 빚으로 쌓이지 않았다


def test_retry_after_is_proportional_to_rate(clock):
    limiter = RateLimiter(rate=2.0, capacity=1, clock=clock)
    limiter.allow("alice")
    assert limiter.allow("alice")[1] == pytest.approx(0.5)


def test_partial_refill_shortens_retry_after(clock):
    limiter = RateLimiter(rate=1.0, capacity=1, clock=clock)
    limiter.allow("alice")
    clock.advance(0.25)
    allowed, retry_after = limiter.allow("alice")
    assert allowed is False
    assert retry_after == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# 리필
# ---------------------------------------------------------------------------


def test_tokens_refill_over_time(clock):
    limiter = RateLimiter(rate=2.0, capacity=4, clock=clock)
    for _ in range(4):
        limiter.allow("alice")
    assert limiter.tokens("alice") == pytest.approx(0.0)

    clock.advance(1.0)  # 2개 찬다
    assert limiter.tokens("alice") == pytest.approx(2.0)
    assert limiter.allow("alice") == (True, 0.0)
    assert limiter.allow("alice") == (True, 0.0)
    assert limiter.allow("alice")[0] is False


def test_tokens_never_exceed_capacity(clock):
    limiter = RateLimiter(rate=10.0, capacity=3, clock=clock)
    limiter.allow("alice")
    clock.advance(3600.0)  # 한 시간을 쉬어도
    assert limiter.tokens("alice") == 3.0
    assert [limiter.allow("alice")[0] for _ in range(4)] == [True, True, True, False]


def test_fractional_tokens_accumulate(clock):
    limiter = RateLimiter(rate=1.0, capacity=1, clock=clock)
    limiter.allow("alice")
    clock.advance(0.5)
    assert limiter.allow("alice")[0] is False
    clock.advance(0.5)
    assert limiter.allow("alice")[0] is True


# ---------------------------------------------------------------------------
# 키별 분리와 cost
# ---------------------------------------------------------------------------


def test_keys_have_independent_buckets(clock):
    limiter = RateLimiter(rate=1.0, capacity=1, clock=clock)
    assert limiter.allow("alice")[0] is True
    assert limiter.allow("alice")[0] is False
    assert limiter.allow("bob")[0] is True  # alice 가 다 써도 bob 은 영향 없음


def test_cost_consumes_multiple_tokens(clock):
    limiter = RateLimiter(rate=1.0, capacity=5, clock=clock)
    assert limiter.allow("agent", cost=3) == (True, 0.0)
    assert limiter.tokens("agent") == 2.0
    allowed, retry_after = limiter.allow("agent", cost=3)
    assert allowed is False
    assert retry_after == pytest.approx(1.0)  # 2개 있고 3개 필요 → 1개분


@pytest.mark.parametrize("cost", [0, -1, 6])
def test_invalid_cost_is_rejected(cost, clock):
    limiter = RateLimiter(rate=1.0, capacity=5, clock=clock)
    with pytest.raises(ValueError):
        limiter.allow("alice", cost=cost)


# ---------------------------------------------------------------------------
# Retry-After 헤더
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("seconds, expected", [(0.0, "1"), (0.3, "1"), (1.0, "1"), (2.0, "2"), (2.1, "3"), (59.99, "60")])
def test_retry_after_header_rounds_up_to_whole_seconds(seconds, expected):
    assert retry_after_header(seconds) == expected
