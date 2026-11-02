"""13단원: TTL(time to live, 수명)이 있는 키-값(key-value) 캐시.

Redis 의 `SET key value EX 60` 을 딕셔너리 하나로 흉내 낸다. 값마다 "언제 만료되는가"를 함께 기억하고,
만료된 값은 없는 것처럼 다룬다.

시계는 생성자로 **주입**한다 (`clock=time.monotonic` 이 기본). 테스트는 가짜 시계를 넘겨 "60초 뒤"를 기다리지 않고
숫자만 바꿔서 만든다 — 테스트 규약 "시간·난수는 주입한다" 의 첫 실전이다. `time.monotonic` 은 뒤로 가지 않는 시계다.

TODO 는 set, get, purge_expired 세 개.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Hashable


class TtlCache:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._items: dict[Hashable, tuple[Any, float]] = {}

    def set(self, key: Hashable, value: Any, ttl_seconds: float) -> None:
        """값을 저장한다. ttl_seconds 가 0 이하면 ValueError. 만료 시각 = 지금 + ttl_seconds.

        힌트: self._items[key] = (value, 만료시각)
        """
        # TODO
        raise NotImplementedError

    def get(self, key: Hashable, default: Any = None) -> Any:
        """값을 돌려준다. 없거나 **만료되었으면** default. 만료된 항목은 이때 지운다 (lazy expiration).

        만료 판정: 지금 >= 만료시각  (정확히 만료 시각이면 만료된 것으로 본다)
        """
        # TODO
        raise NotImplementedError

    def delete(self, key: Hashable) -> None:
        self._items.pop(key, None)

    def purge_expired(self) -> int:
        """만료된 항목을 모두 지우고 지운 개수를 돌려준다 (active expiration).

        함정: 딕셔너리를 순회하면서 지우면 RuntimeError. 지울 키를 먼저 리스트로 모은 뒤 지운다.
        """
        # TODO
        raise NotImplementedError

    def __contains__(self, key: Hashable) -> bool:
        sentinel = object()
        return self.get(key, sentinel) is not sentinel

    def __len__(self) -> int:
        self.purge_expired()
        return len(self._items)
