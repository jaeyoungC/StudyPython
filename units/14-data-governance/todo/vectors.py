"""14단원: 임베딩(embedding)·벡터 검색의 최소 개념 — 외부 라이브러리 없이.

임베딩은 텍스트를 숫자 벡터로 바꾼 것이고, "의미가 비슷하다" 를 "벡터의 방향이 비슷하다(코사인 유사도가 높다)" 로 근사한다.
46단원(RAG)에서 진짜 임베딩 모델을 쓰기 전에, 여기서는 **벡터가 이미 있다고 치고** 검색 부분만 만든다.
"""

from __future__ import annotations

import math
from typing import Hashable, Sequence

Vector = Sequence[float]


def dot(a: Vector, b: Vector) -> float:
    """내적. 길이가 다르면 ValueError."""
    # TODO
    raise NotImplementedError


def cosine_similarity(a: Vector, b: Vector) -> float:
    """-1.0 ~ 1.0. 같은 방향이면 1, 직교하면 0, 반대면 -1. 영벡터가 섞이면 ValueError (0 으로 나눌 수 없다)."""
    # TODO
    raise NotImplementedError


def top_k(query: Vector, items: Sequence[tuple[Hashable, Vector]], k: int) -> list[tuple[Hashable, float]]:
    """(id, 벡터) 목록에서 query 와 코사인 유사도가 높은 순으로 k 개 (id, 유사도). 동점이면 먼저 나온 것이 앞."""
    # TODO
    raise NotImplementedError
