# StudyPython

Python 기초 문법을 아는 상태에서 출발해, 소프트웨어 엔지니어링 기초(데이터 · 아키텍처 · 신뢰성 · 운영)와
코딩 에이전트 활용까지 12주 동안 쌓아 가는 학습 저장소입니다.

학습 노트: [Andrew Ng: 코딩은 더 이상 병목이 아니다 — 초급 아키텍트 학습 노트](https://claude.ai/artifact/TYZGvjwyDU6SfNaraeA1vp)
(노트의 "학습 로드맵 (12주 일정)" 표에서 주차별 상태를 관리합니다.)

## 방식

- **하나의 프로그램을 12주 동안 키웁니다.** 메모리에만 있던 "할 일 관리" 프로그램이 파일 → SQLite → API →
  신뢰성 장치 → 로그·CI 순으로 자랍니다. 매주 이전 주차 코드를 복사해 와서 이어 만드세요.
- **주 6~10시간 기준**: 개념 공부 2~3시간, 실습 3~5시간, 정리(ADR·회고) 1시간.
- **먼저 내 답을 적고 AI와 비교합니다.** 노트의 "챗봇 의존의 함정"을 피하려는 규칙입니다.
  이 저장소의 `CLAUDE.md`는 Claude가 정답 코드를 바로 주지 않고 힌트부터 주도록 설정해 두었습니다.
- **매주 결정 하나를 ADR로 남깁니다.** 템플릿: [`docs/adr/0000-template.md`](docs/adr/0000-template.md)

## 12주 일정

| 주차 | 주제 | 노트의 영역 | 폴더 |
| --- | --- | --- | --- |
| 1 | 함수·자료구조·pytest 입문 | 기초 다지기 | [week01](weeks/week01) |
| 2 | 클래스·dataclass·타입 힌트·예외 | 1. 풀스택 앱 (상태 관리) | [week02](weeks/week02) |
| 3 | 파일 입출력·JSON·첫 ADR | 2. 데이터 관리 (영속화) | [week03](weeks/week03) |
| 4 | SQL 기초와 sqlite3 | 2. 데이터 관리 | [week04](weeks/week04) |
| 5 | 접근 패턴·정규화·인덱스 | 2. 데이터 관리 | [week05](weeks/week05) |
| 6 | 트랜잭션·동시성·마이그레이션 | 2. 데이터 관리 | [week06](weeks/week06) |
| 7 | 계층 분리와 상태의 위치 | 3. 시스템 아키텍처 | [week07](weeks/week07) |
| 8 | HTTP API 설계 (FastAPI) | 1. 풀스택 앱 (API 설계) | [week08](weeks/week08) |
| 9 | 테스트 전략·타임아웃·재시도·멱등성 | 4. 보안과 신뢰성 | [week09](weeks/week09) |
| 10 | 속도 제한·점진적 기능 저하 | 4. 보안과 신뢰성 | [week10](weeks/week10) |
| 11 | 로그·지표·CI | 5. 운영과 확장 | [week11](weeks/week11) |
| 12 | 코딩 에이전트 활용·사용자 인터뷰 | 에이전트 워크플로, 빌드 방향 잡기 | [week12](weeks/week12) |

1~3주차는 시작 코드와 테스트가 들어 있습니다. 4주차부터는 과제 설명만 있고, 해당 주차가 되면 시작 코드를 함께 만듭니다.

## 실행

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

pytest weeks/week01        # 이번 주 테스트만 실행
python weeks/week01/todo_memory.py   # CLI 직접 실행
```

처음에는 테스트가 실패하는 것이 정상입니다. `TODO`를 채워 모두 통과시키는 것이 그 주의 목표입니다.

## 한 주를 마치는 기준

1. 그 주 테스트가 모두 통과한다.
2. `weeks/weekNN/NOTES.md`에 "배운 것 3가지 / 헷갈린 것 1가지 / 다음 주에 바꿀 것"을 적었다.
3. 그 주에 내린 설계 결정 하나를 `docs/adr/`에 남겼다 (3주차부터).
4. 학습 노트의 일정표 상태를 "완료"로 바꿨다.
