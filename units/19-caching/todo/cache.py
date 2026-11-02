"""앱 안의 캐시 (19단원). 과제: get / set / delete_prefix 의 TODO 를 채우세요.

캐시는 "같은 질문에 같은 답을 다시 계산하지 않기"입니다. 대가는 두 가지입니다.
- 최신성(freshness): 원본이 바뀌었는데 캐시가 옛 값을 돌려줄 수 있다 → 무효화(invalidation)가 필요하다.
- 메모리: 무한히 쌓이면 안 된다 → 크기 제한이나 TTL 이 필요하다 (이 단원은 크기 제한만).

MemoryCache 는 dict 를 감싼 가장 단순한 형태입니다. hits/misses 를 세어 두는 이유는
"캐시를 넣었더니 빨라졌다"가 아니라 "적중률이 몇 %다"로 말하기 위해서입니다 (10단원의 측정 습관).
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Any

_MISSING = object()


class MemoryCache:
    def __init__(self, max_items: int = 1024) -> None:
        self.max_items = max_items
        self._data: OrderedDict[str, Any] = OrderedDict()  # 삽입 순서를 기억 → 가장 오래된 것부터 내보낸다
        self.hits = 0
        self.misses = 0

    def get(self, key: str, default: Any = None) -> Any:
        """없으면 misses+1 후 default. 있으면 hits+1, move_to_end(key) 로 "최근 사용" 표시 후 값."""
        # TODO
        raise NotImplementedError

    def set(self, key: str, value: Any) -> None:
        """저장하고 맨 뒤로. max_items 를 넘으면 맨 앞(가장 오래 안 쓴 것)부터 popitem(last=False)."""
        # TODO
        raise NotImplementedError

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def delete_prefix(self, prefix: str) -> int:
        """prefix 로 시작하는 키를 모두 지우고 지운 개수를 돌려준다."""
        # TODO
        raise NotImplementedError

    def clear(self) -> None:
        self._data.clear()

    def __len__(self) -> int:
        return len(self._data)

    def stats(self) -> dict[str, float | int]:
        total = self.hits + self.misses
        return {"hits": self.hits, "misses": self.misses, "size": len(self._data), "hit_rate": (self.hits / total) if total else 0.0}
