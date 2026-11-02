# 4주차 — SQL 기초와 sqlite3

## 목표

JSON 파일 대신 SQLite 데이터베이스에 할 일을 저장합니다. 3주차 ADR의 대안이었던 SQLite를 직접 써 보고 비교합니다.

## 공부할 개념

- 테이블, 기본 키(PRIMARY KEY), `NOT NULL`, `CHECK`
- `INSERT / SELECT / UPDATE / DELETE`, `WHERE`, `ORDER BY`
- Python `sqlite3`: 연결, 커서, `?` 자리표시자로 값 넣기 (SQL 인젝션을 막는 이유)
- `AUTOINCREMENT` 와 `lastrowid`

참고: [sqlite3 문서](https://docs.python.org/ko/3/library/sqlite3.html), [SQLite 튜토리얼](https://www.sqlitetutorial.net/)

## 과제

`sqlite_store.py` 에 `SqliteTaskStore` 클래스를 만드세요: `add(title)`, `get(id)`, `complete(id)`, `remove(id)`, `list(only_open=False)`.
테스트는 `sqlite3.connect(":memory:")` 로 실제 파일 없이 돌립니다. 테스트도 직접 먼저 써 보세요 (1~3주차 테스트를 참고).

## 스스로 답해 볼 질문

1. `f"... WHERE id = {task_id}"` 처럼 문자열로 SQL을 만들면 어떤 위험이 있나요?
2. 할 일 하나를 완료할 때 JSON 방식과 SQLite 방식은 각각 얼마나 많은 데이터를 다시 쓰나요?
3. 3주차 ADR-0001을 지금 다시 쓴다면 무엇이 달라지나요? → ADR-0002 (JSON → SQLite 전환)

## 완료 기준

- [ ] 직접 쓴 테스트가 모두 통과
- [ ] ADR-0002 작성
