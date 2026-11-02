"""32단원 테스트 뼈대. 실행: pytest units/32-metrics-and-tracing

본문을 채우세요. 시간은 FakeClock 으로 주입합니다.
"""

import pytest

from metrics import Counter, Histogram, Registry, timed


class FakeClock:
    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


# ---------------------------------------------------------------------------
# Counter
# ---------------------------------------------------------------------------


def test_counter_starts_at_zero_and_increments():
    """value() 는 0.0 에서 시작하고 inc() 두 번이면 2.0, inc(3) 이면 5.0."""
    pytest.fail("아직 구현하지 않음")


def test_counter_tracks_label_combinations_separately():
    """labels=("method","status") 로 GET/200 을 2번, POST/201 을 1번 세면 각각 2.0, 1.0 이고 모르는 조합은 0.0."""
    pytest.fail("아직 구현하지 않음")


def test_counter_rejects_negative_increment():
    """inc(-1) 은 ValueError. 카운터는 내려가지 않는다."""
    pytest.fail("아직 구현하지 않음")


def test_counter_render_matches_prometheus_text_format():
    """render() 의 정확한 문자열을 비교한다: HELP, TYPE, 라벨 줄 순서, 마지막 줄바꿈."""
    pytest.fail("아직 구현하지 않음")


# ---------------------------------------------------------------------------
# Histogram
# ---------------------------------------------------------------------------


def test_histogram_count_and_sum():
    """0.1, 0.2, 0.3 을 observe 하면 count 3, sum 0.6 (pytest.approx)."""
    pytest.fail("아직 구현하지 않음")


def test_histogram_buckets_are_cumulative():
    """buckets=(0.1, 0.5, 1.0) 에 0.05, 0.3, 0.7, 2.0 을 넣으면 le=0.1 → 1, le=0.5 → 2, le=1.0 → 3, +Inf → 4. render() 로 확인."""
    pytest.fail("아직 구현하지 않음")


def test_percentile_nearest_rank():
    """1..100 을 넣으면 p50 == 50, p95 == 95, p100 == 100, p0 은 1 (또는 정의한 규칙대로)."""
    pytest.fail("아직 구현하지 않음")


def test_percentile_of_empty_histogram_is_none():
    """관측값이 없으면 None."""
    pytest.fail("아직 구현하지 않음")


def test_p95_is_dominated_by_slow_tail():
    """빠른 요청 95개(0.01)와 느린 요청 5개(2.0) → p50 은 0.01 인데 p95 는 0.01 이고 p96 은 2.0. 평균은 0.11.
    '평균은 괜찮은데 사용자는 느리다' 가 왜 생기는지 숫자로 본다."""
    pytest.fail("아직 구현하지 않음")


# ---------------------------------------------------------------------------
# Registry 와 timed
# ---------------------------------------------------------------------------


def test_registry_renders_metrics_in_registration_order():
    """Counter 와 Histogram 을 등록하면 render_text() 에 그 순서로 나온다."""
    pytest.fail("아직 구현하지 않음")


def test_registry_rejects_duplicate_names():
    """같은 이름을 두 번 register 하면 ValueError."""
    pytest.fail("아직 구현하지 않음")


def test_timed_observes_elapsed_time_using_injected_clock():
    """with timed(h, clock=fake): fake.advance(0.25) → h.count == 1, h.sum ≈ 0.25."""
    pytest.fail("아직 구현하지 않음")


def test_timed_records_even_when_block_raises():
    """블록 안에서 예외가 나도 관측은 기록되고 예외는 전파된다."""
    pytest.fail("아직 구현하지 않음")
