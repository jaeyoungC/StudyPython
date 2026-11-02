"""32단원: 지표(metrics) — 카운터, 히스토그램, 백분위수, /metrics 텍스트 형식.

로그(31단원)는 "무슨 일이 있었나"를, 지표는 "얼마나 자주·얼마나 느리게"를 숫자로 답합니다.
이 모듈은 외부 라이브러리 없이 최소한의 레지스트리를 만들어 Prometheus 텍스트 형식으로 내보냅니다.

뼈대만 있습니다. test_unit32.py 의 뼈대를 먼저 채운 뒤 구현하세요.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Callable, Iterator


class Counter:
    """단조 증가하는 수. 예: http_requests_total{method="GET",path="/tasks",status="200"}

    - labels 는 라벨 이름의 튜플. inc(**label_values) 로 라벨 조합별로 센다
    - 값은 줄어들지 않는다. inc(amount) 의 amount < 0 이면 ValueError
    """

    def __init__(self, name: str, help: str, labels: tuple[str, ...] = ()) -> None:
        # TODO
        raise NotImplementedError

    def inc(self, amount: float = 1.0, **label_values: str) -> None:
        # TODO
        raise NotImplementedError

    def value(self, **label_values: str) -> float:
        """해당 라벨 조합의 현재 값. 없으면 0.0"""
        # TODO
        raise NotImplementedError

    def render(self) -> str:
        """Prometheus 텍스트 형식.
        # HELP name help
        # TYPE name counter
        name{method="GET",path="/tasks"} 3
        라벨이 없으면 name 3. 라벨은 선언 순서대로, 값은 큰따옴표. 마지막에 줄바꿈 하나.
        """
        # TODO
        raise NotImplementedError


class Histogram:
    """관측값(예: 요청 지연 초)을 버킷에 세고, 백분위수(percentile)를 계산한다.

    - buckets 는 오름차순 상한 (예: (0.005, 0.01, 0.05, 0.1, 0.5, 1.0)). 마지막에 +Inf 는 자동
    - observe(v) 는 v 이하인 모든 버킷(누적)과 _count, _sum 을 갱신하고, 백분위수 계산을 위해 원시 값도 보관한다
      (운영용 라이브러리는 원시 값을 보관하지 않고 버킷으로 근사한다 — README 참고)
    - percentile(p) : 0 <= p <= 100. 관측값을 정렬해 nearest-rank 방식: 정렬된 값의 ceil(p/100 * n) 번째 (1부터). 관측값이 없으면 None
    """

    def __init__(self, name: str, help: str, buckets: tuple[float, ...] = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)) -> None:
        # TODO
        raise NotImplementedError

    def observe(self, value: float) -> None:
        # TODO
        raise NotImplementedError

    @property
    def count(self) -> int:
        # TODO
        raise NotImplementedError

    @property
    def sum(self) -> float:
        # TODO
        raise NotImplementedError

    def percentile(self, p: float) -> float | None:
        # TODO
        raise NotImplementedError

    def render(self) -> str:
        """Prometheus 텍스트 형식.
        # HELP name help
        # TYPE name histogram
        name_bucket{le="0.005"} 0
        ...
        name_bucket{le="+Inf"} 7
        name_sum 1.23
        name_count 7
        """
        # TODO
        raise NotImplementedError


class Registry:
    """이름 → 지표. render_text() 가 /metrics 응답 본문이 된다. 같은 이름을 두 번 등록하면 ValueError."""

    def __init__(self) -> None:
        # TODO
        raise NotImplementedError

    def register(self, metric: Counter | Histogram) -> None:
        # TODO
        raise NotImplementedError

    def render_text(self) -> str:
        """등록 순서대로 각 지표의 render() 를 이어 붙인다."""
        # TODO
        raise NotImplementedError


@contextmanager
def timed(histogram: Histogram, clock: Callable[[], float] = time.perf_counter) -> Iterator[None]:
    """with timed(h): ... 블록의 소요 시간을 histogram 에 observe 한다. 예외가 나도 기록한다."""
    # TODO
    raise NotImplementedError
    yield  # pragma: no cover
