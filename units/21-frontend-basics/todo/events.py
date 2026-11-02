"""도메인 이벤트 (20단원): "무슨 일이 있었다"를 값으로 적은 것.

서비스는 이벤트를 **발행**만 하고, 그 뒤에 누가 무엇을 하는지(알림, 로그, 통계) 모른다.
그래서 알림 발송이 느리거나 실패해도 complete() 는 느려지거나 실패하지 않는다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    type: str  # 예: "task.completed"
    task_id: int
    owner_id: int | None
    title: str
