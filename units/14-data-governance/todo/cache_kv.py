"""TTL 이 있는 키-값 캐시 (13단원 완성본)."""

from __future__ import annotations

import time
from typing import Any, Callable, Hashable


class TtlCache:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._items: dict[Hashable, tuple[Any, float]] = {}

    def set(self, key: Hashable, value: Any, ttl_seconds: float) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds 는 0 보다 커야 합니다")
        self._items[key] = (value, self._clock() + ttl_seconds)

    def get(self, key: Hashable, default: Any = None) -> Any:
        item = self._items.get(key)
        if item is None:
            return default
        value, expires_at = item
        if self._clock() >= expires_at:
            del self._items[key]
            return default
        return value

    def delete(self, key: Hashable) -> None:
        self._items.pop(key, None)

    def purge_expired(self) -> int:
        now = self._clock()
        expired = [key for key, (_, expires_at) in self._items.items() if now >= expires_at]
        for key in expired:
            del self._items[key]
        return len(expired)

    def __contains__(self, key: Hashable) -> bool:
        sentinel = object()
        return self.get(key, sentinel) is not sentinel

    def __len__(self) -> int:
        self.purge_expired()
        return len(self._items)
