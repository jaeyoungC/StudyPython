# 1주차 — 함수 · 자료구조 · pytest 입문

## 목표

메모리에만 저장하는 "할 일 목록" 프로그램을 함수로 나눠 만들고, 테스트로 동작을 확인하는 습관을 들입니다.

## 공부할 개념 (2~3시간)

- `list`, `dict` 다루기: 추가, 검색, 수정, 삭제, 컴프리헨션
- 함수 설계: 입력·출력이 분명한 함수, 부작용(side effect)이 무엇인지
- 예외: `raise ValueError(...)`, `try / except`
- pytest: `assert`, `pytest.raises`, 테스트 이름 짓기

참고: [Python 공식 튜토리얼 5장 자료구조](https://docs.python.org/ko/3/tutorial/datastructures.html),
[pytest 시작하기](https://docs.pytest.org/en/stable/getting-started.html)

## 과제 (3~5시간)

`todo_memory.py` 의 `TODO` 를 채워 `pytest weeks/week01` 을 모두 통과시키세요.

할 일 하나는 이런 딕셔너리입니다.

```python
{"id": 1, "title": "SQL 공부", "done": False}
```

| 함수 | 하는 일 |
| --- | --- |
| `add_task(tasks, title)` | 새 할 일을 추가하고 반환. id는 기존 최대 id + 1 (비어 있으면 1). 제목 앞뒤 공백 제거, 빈 제목이면 `ValueError` |
| `find_task(tasks, task_id)` | id로 찾아 반환. 없으면 `ValueError` |
| `complete_task(tasks, task_id)` | `done` 을 `True` 로 바꾸고 반환 |
| `remove_task(tasks, task_id)` | 목록에서 지우고 지운 할 일을 반환 |
| `list_tasks(tasks, only_open=False)` | 전체 또는 미완료 할 일만 새 리스트로 반환 |

다 통과하면 `python weeks/week01/todo_memory.py` 로 직접 써 보세요.

## 스스로 답해 볼 질문

1. 왜 id를 `len(tasks) + 1` 이 아니라 "최대 id + 1" 로 정할까요? (삭제 후 추가를 떠올려 보세요)
2. 프로그램을 껐다 켜면 할 일이 사라집니다. 이것을 해결하려면 무엇이 필요할까요? → 3주차
3. `list_tasks` 가 원본 리스트가 아니라 새 리스트를 돌려주면 무엇이 좋을까요?

## 완료 기준

- [ ] `pytest weeks/week01` 전부 통과
- [ ] 테스트를 하나 직접 추가 (예: 같은 할 일을 두 번 완료하면?)
- [ ] `NOTES.md` 에 배운 것 3가지 / 헷갈린 것 1가지 / 다음 주에 바꿀 것
