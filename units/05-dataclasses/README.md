# 05 — dataclass · 타입 힌트 · 직렬화

## 목표

04단원의 `Task`를 `@dataclass`로 다시 쓰고, 타입 힌트를 읽고 쓸 수 있게 되며, `Task` 객체를 딕셔너리로(그리고 다시 객체로) 바꾸는
**직렬화(serialization)** 를 익힙니다. 직렬화는 07단원(파일 저장)과 17단원(HTTP API)의 토대입니다.

## 노트와의 연결

노트는 "컨텍스트 파일에 코드베이스 정보, 아키텍처 가정, 스타일, 데이터 접근 패턴을 적어 둔다"고 합니다.
타입 힌트는 코드 안에 적는 가장 작은 컨텍스트입니다. 사람에게도, 편집기에게도, 코딩 에이전트에게도
"이 함수는 `Task`를 받아 `dict`를 돌려준다"를 설명 없이 전달합니다.

## 공부할 개념

| 개념 | 핵심 | 참고 |
| --- | --- | --- |
| `@dataclass` | 속성 목록만 적으면 `__init__`, `__repr__`, `__eq__`를 만들어 준다. 검증은 `__post_init__`에서 | [dataclasses 문서](https://docs.python.org/ko/3/library/dataclasses.html) |
| 타입 힌트(type hint) | `list[Task]`, `dict[str, int]`, `Task \| None`(없을 수도 있음), 반환 `-> int`. 실행에는 영향 없음 | [typing 문서](https://docs.python.org/ko/3/library/typing.html) |
| 직렬화 | 객체 → 딕셔너리(`dataclasses.asdict`) → 나중에 JSON. 반대 방향 `from_dict`는 직접 쓴다(검증 포함) | 같은 dataclasses 문서의 `asdict` |

### `field(default_factory=list)`가 필요한 이유

```python
@dataclass
class Bad:
    tags: list = []            # 오류! 모든 인스턴스가 같은 리스트를 공유하게 된다

@dataclass
class Good:
    tags: list[str] = field(default_factory=list)   # 인스턴스마다 새 리스트
```

`TaskList`의 내부 리스트도 같은 이유로 `field(default_factory=list)`를 씁니다.

## 과제

`todo_dataclass.py`의 `TODO`를 채워 `pytest units/05-dataclasses`를 통과시키세요.

| 항목 | 하는 일 |
| --- | --- |
| `@dataclass class Task` | `id: int`, `title: str`, `done: bool = False`. `__post_init__`에서 공백 제거·빈 제목 검사 |
| `Task.complete()` | 04단원과 같음 |
| `Task.to_dict()` | `{"id": 1, "title": "산책", "done": False}` |
| `Task.from_dict(data)` | 딕셔너리에서 `Task`를 만든다. 키가 빠졌거나 타입이 틀리면 `ValueError`. `@classmethod` |
| `@dataclass class TaskList` | `_tasks: list[Task] = field(default_factory=list)`. 04단원의 메서드 + `find(title) -> Task \| None` + `__len__` + `__iter__` |

`find(title)`는 제목이 정확히 같은 첫 할 일을 돌려주고, 없으면 `None`입니다. "없음"을 예외로 알릴지 `None`으로 알릴지의 차이를 느껴 보세요.
`__len__`을 정의하면 `len(tasks)`가, `__iter__`를 정의하면 `for task in tasks:`가 됩니다. 04단원의 `count()`는 `__len__`으로 바뀝니다.

## 스스로 답해 볼 질문

1. `get(id)`는 없으면 예외, `find(title)`는 없으면 `None`. 어떤 기준으로 둘 중 하나를 고를까요?
2. `from_dict`에 검증이 없으면, 07단원에서 손으로 고친 JSON 파일이 들어왔을 때 어디서 문제가 터질까요?
3. `@dataclass`가 만들어 준 `__eq__` 때문에 `Task(1, "a") == Task(1, "a")`가 `True`입니다. 그런데 `get()`은 여전히 `is`로 같은 객체를 돌려줘야 합니다. 둘의 차이가 중요한 상황을 하나 생각해 보세요.
4. `Task | None`을 돌려주는 함수를 쓰는 쪽은 무엇을 반드시 해야 하나요?

## 함정

- `__post_init__`에서 `self.title = self.title.strip()`처럼 **대입**해야 바뀝니다.
- `asdict()`는 중첩된 dataclass도 재귀적으로 바꿉니다. 지금은 괜찮지만 큰 객체에서는 비용이 큽니다.
- `from_dict`에서 `data["id"]`가 문자열 `"1"`로 들어오면? `int`인지 확인하세요. 테스트가 이것을 봅니다.

## 완료 기준

- [ ] `pytest units/05-dataclasses` 전부 통과
- [ ] 04단원의 CLI가 05단원 `TaskList`로도 그대로 동작 (`count()` → `len()`만 바꾸면 되는지 확인)
- [ ] `NOTES.md`: 질문 1~4의 내 답, 배운 것 3가지, 헷갈린 것 1가지
- [ ] 브랜치 `unit-05` → PR → 머지

## 더 깊이

- `@dataclass(frozen=True)`로 만들면 무엇이 달라지고, `complete()`는 어떻게 바꿔야 할까요? 불변(immutable) 객체가 유리한 상황은?
- `mypy` 또는 `pyright`를 설치해 `todo_dataclass.py`를 검사해 보세요. 타입 힌트가 "메모"에서 "검사기"로 바뀝니다.
