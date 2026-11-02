"""02단원: 버그가 있는 함수 네 개.

테스트(test_unit02.py)는 올바릅니다. 이 파일만 고쳐서 테스트를 통과시키세요.
고치기 전에 NOTES.md에 "어느 줄 / 기대 / 실제 / 원인"을 먼저 적습니다.
"""

from pathlib import Path
from typing import Callable


def average(numbers: list[float]) -> float:
    """숫자 리스트의 평균. 빈 리스트면 ValueError."""
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)


def parse_age(text: str) -> int:
    """문자열을 나이(정수)로 바꾼다.

    - 앞뒤 공백은 허용한다 ("  30 " → 30)
    - 숫자가 아니거나 0~150 범위 밖이면 ValueError
    """
    if not text.isdigit():
        raise ValueError(f"숫자가 아닙니다: {text!r}")
    age = int(text)
    if age < 0 or age > 150:
        raise ValueError(f"범위 밖: {age}")
    return age


def count_words(path: Path) -> int:
    """텍스트 파일의 단어 수를 센다 (공백 기준)."""
    count = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            count += len(line.split(" "))
    return count


def greeting(name: str, now: Callable[[], int]) -> str:
    """now()가 돌려준 시(0~23)가 12보다 작으면 아침 인사, 아니면 일반 인사.

    now를 인자로 받는 이유: 테스트에서 시간을 마음대로 정하기 위해서입니다.
    """
    if now() < 12:
        return f"좋은 아침, {name}"
    else:
        return f"안녕하세요 {name}"
