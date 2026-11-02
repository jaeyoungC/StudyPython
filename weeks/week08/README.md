# 8주차 — HTTP API 설계 (FastAPI)

## 목표

할 일 서비스를 HTTP API로 엽니다. 7주차의 서비스 계층을 그대로 재사용하는지가 구조 설계의 시험대입니다.

## 공부할 개념

- HTTP 메서드와 상태 코드: `GET / POST / PATCH / DELETE`, `200 / 201 / 400 / 404 / 422`
- 리소스 중심 URL 설계: `/tasks`, `/tasks/{id}`, `/tasks?done=false`
- 요청·응답 스키마(Pydantic), 입력 검증
- 페이지네이션: `limit`, `offset` (또는 커서) — 노트의 "에이전트는 사람보다 훨씬 많이 호출한다"
- `fastapi.testclient.TestClient` 로 API 테스트

준비: `requirements.txt` 의 fastapi, uvicorn, httpx 주석을 풀고 설치

## 과제

1. 코드 전에 API 명세를 표로 쓰기 (메서드, 경로, 요청, 응답, 오류)
2. FastAPI로 구현하고 `uvicorn app:app --reload` 로 실행, `/docs` 에서 직접 호출
3. 없는 id → 404, 빈 제목 → 422 가 나오는지 테스트

## 스스로 답해 볼 질문

1. 완료 처리는 `PATCH /tasks/{id}` 와 `POST /tasks/{id}/complete` 중 무엇이 좋을까요? 근거는?
2. 목록 API에 페이지네이션이 없으면 할 일 100만 개일 때 무슨 일이 생길까요?

## 완료 기준

- [ ] API 테스트 통과
- [ ] ADR-0006: API 설계 결정 (URL, 완료 처리 방식)
