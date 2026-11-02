# 03 — 함수와 자료구조

## 목표

메모리에만 저장하는 "할 일 목록" 프로그램을 **입력과 출력이 분명한 함수** 여러 개로 나눠 만들고,
테스트로 동작을 확인합니다. 이 프로그램이 54단원까지 자라는 씨앗입니다.

## 노트와의 연결

노트는 "문법 암기의 가치는 줄지만, 소프트웨어가 어떻게 동작하는지 깊이 아는 사람이 크게 앞선다"고 합니다.
이 단원은 문법이 아니라 **"이 함수는 무엇을 바꾸고 무엇을 돌려주는가"를 분명히 하는 습관**을 기릅니다.
그 습관이 나중에 에이전트에게 줄 스펙의 정확도가 됩니다.

## 공부할 개념

| 개념 | 핵심 | 참고 |
| --- | --- | --- |
| list와 dict 다루기 | 추가·검색·수정·삭제, 컴프리헨션 `[x for x in xs if ...]` | [공식 튜토리얼 5장 자료구조](https://docs.python.org/ko/3/tutorial/datastructures.html) |
| 함수 설계와 부작용(side effect) | 인자로 받은 리스트를 **바꾸는** 함수와 **새 리스트를 돌려주는** 함수의 차이 | [튜토리얼 4.8 함수 정의](https://docs.python.org/ko/3/tutorial/controlflow.html#defining-functions) |
| 예외 던지기 | 잘못된 입력에는 `None`을 돌려주지 말고 `raise ValueError("이유")` | [튜토리얼 8장 오류와 예외](https://docs.python.org/ko/3/tutorial/errors.html) |

02단원에서 본 pytest 기능이 그대로 쓰입니다: `assert`, `pytest.raises`, `@pytest.mark.parametrize`.
테스트 안의 `is` 는 "같은 객체인가", `==` 는 "값이 같은가"입니다. `find_task` 가 복사본이 아니라 **그 객체**를 돌려줘야 하므로 `is` 로 확인합니다.

시작 코드의 `tasks: list[dict]` 같은 표기는 **타입 힌트(type hint)** 입니다. 실행에는 영향이 없고 "이 인자는 딕셔너리의 리스트"라고 사람과 도구에게 알려 주는 메모입니다. 05단원에서 제대로 다룹니다.

## 과제

`todo_memory.py` 의 `TODO` 를 채워 `pytest units/03-functions` 을 모두 통과시키세요.

할 일 하나는 이런 딕셔너리입니다.

```python
{"id": 1, "title": "SQL 공부", "done": False}
```

| 함수 | 하는 일 |
| --- | --- |
| `add_task(tasks, title)` | 새 할 일을 `tasks` 끝에 추가하고 반환. id는 기존 최대 id + 1 (비어 있으면 1). 제목 앞뒤 공백 제거, 빈 제목이면 `ValueError` |
| `find_task(tasks, task_id)` | id로 찾아 **그 객체**를 반환. 없으면 `ValueError` |
| `complete_task(tasks, task_id)` | `done` 을 `True` 로 바꾸고 반환 |
| `remove_task(tasks, task_id)` | 목록에서 지우고 지운 할 일을 반환 |
| `list_tasks(tasks, only_open=False)` | 전체 또는 미완료 할 일만 **새 리스트**로 반환 |

다 통과하면 `python units/03-functions/todo_memory.py` 로 직접 써 보세요.

## 스스로 답해 볼 질문

1. 왜 id를 `len(tasks) + 1` 이 아니라 "최대 id + 1" 로 정할까요? (삭제 후 추가를 떠올려 보세요)
2. 프로그램을 껐다 켜면 할 일이 사라집니다. 이것을 해결하려면 무엇이 필요할까요? → 07단원
3. `list_tasks` 가 원본 리스트가 아니라 새 리스트를 돌려주면 무엇이 좋을까요? 호출한 쪽이 결과를 `.clear()` 하면?
4. 다섯 함수 모두 첫 인자로 `tasks` 를 받습니다. 이 "항상 같이 다니는 데이터와 함수"를 묶는 방법이 있을까요? → 04단원

## 함정

- `title.strip()` 은 **새 문자열을 돌려줍니다.** 원래 변수는 바뀌지 않으니 결과를 다시 받아야 합니다.
- 리스트를 `for` 로 돌면서 그 리스트에서 `remove` 하면 항목을 건너뜁니다. 먼저 찾고, 루프 밖에서 지우세요.
- `max([])` 는 오류입니다. `max(..., default=0)` 을 찾아보세요.

## 완료 기준

- [ ] `pytest units/03-functions` 13개 테스트 전부 통과
- [ ] 테스트를 **2개 직접 추가** (예: 같은 할 일을 두 번 완료하면? 제목이 숫자면?)
- [ ] `NOTES.md` 에 배운 것 3가지 / 헷갈린 것 1가지 / 다음 단원에 바꿀 것
- [ ] 브랜치 `unit-03` 에서 작업하고 PR을 만들어 스스로 리뷰한 뒤 머지 (01단원 의식)

## 더 깊이

- `list_tasks(tasks)` 가 돌려준 리스트 안의 딕셔너리를 수정하면 원본도 바뀝니다. 왜일까요? `copy.deepcopy` 는 언제 필요할까요?
