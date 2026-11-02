# 00 — 개발 환경

## 목표

이 저장소를 내 컴퓨터에서 실행하고, 앞으로 모든 단원에서 쓸 도구(가상 환경, 패키지 설치, 테스트 실행, 편집기)를
한 번 제대로 세팅합니다. 환경 문제로 공부가 멈추는 일을 미리 없애는 단원입니다.

## 노트와의 연결

노트는 운영 영역의 기초로 "의존성 관리"를 꼽습니다. 의존성 관리의 출발점이 "내 프로젝트가 어떤 패키지의 어떤 버전에
기대는지 적어 두고, 다른 컴퓨터에서도 똑같이 재현하는 것"입니다. `requirements.txt`와 가상 환경이 그 가장 작은 형태입니다.

## 공부할 개념

| 개념 | 핵심 | 참고 |
| --- | --- | --- |
| 가상 환경(virtual environment) | 프로젝트마다 독립된 패키지 공간. 시스템 Python을 더럽히지 않는다 | [venv 문서](https://docs.python.org/ko/3/library/venv.html) |
| 패키지 설치와 고정 | `pip install`, `requirements.txt`, 버전 고정(`==`)과 범위(`>=`)의 차이 | [pip 사용자 가이드](https://pip.pypa.io/en/stable/user_guide/) |
| 프로젝트 설정 파일 | `pyproject.toml`이 무엇을 적는 파일인지 (지금은 pytest 설정과 Python 버전만) | [pyproject.toml 안내](https://packaging.python.org/ko/latest/guides/writing-pyproject-toml/) |

## 과제

1. Python 3.12 이상을 설치하고 `python3 --version`으로 확인합니다.
2. 저장소 루트에서 가상 환경을 만들고 활성화합니다.
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. 테스트 도구가 동작하는지 확인합니다. 아직 아무것도 구현하지 않았으니 **실패하는 것이 정상**입니다.
   ```bash
   pytest units/03-functions -q
   ```
   `13 failed` 비슷한 줄이 보이면 성공입니다. `No module named pytest`가 보이면 가상 환경이 활성화되지 않은 것입니다.
4. 편집기(VS Code 권장)에 Python 확장을 설치하고, 인터프리터를 `.venv`로 선택합니다. 테스트 탐색기에서 `units/03-functions`의 테스트가 보이는지 확인합니다.
5. `pip list`로 설치된 패키지를 보고, `requirements.txt`에 적힌 것과 비교해 봅니다.

## 스스로 답해 볼 질문

1. 가상 환경 없이 전역에 패키지를 설치하면 프로젝트가 두 개일 때 어떤 문제가 생길까요?
2. `pytest>=8`과 `pytest==8.3.2`는 무엇이 다른가요? 각각 언제 쓰는 게 좋을까요?
3. 동료(또는 6개월 뒤의 나)가 이 저장소를 받았을 때, 어떤 파일 하나만 보면 환경을 재현할 수 있어야 할까요?

## 함정

- `python`과 `python3`가 서로 다른 버전을 가리키는 컴퓨터가 많습니다. 가상 환경을 활성화한 뒤에는 `python`만 쓰세요.
- `.venv/`는 git에 올리지 않습니다(`.gitignore`에 이미 있음). 올려야 할 것은 "무엇을 설치했는가"이지 설치된 파일 자체가 아닙니다.
- `pip install`을 가상 환경 밖에서 실행하면 경고가 나옵니다. 프롬프트 앞에 `(.venv)`가 보이는지 확인하세요.

## 완료 기준

- [ ] `python --version`이 3.12 이상
- [ ] `(.venv)`가 활성화된 상태에서 `pytest units/03-functions -q`가 "failed"를 출력 (오류가 아니라 실패)
- [ ] 편집기에서 테스트가 탐색됨
- [ ] `NOTES.md`에 설치 중 막혔던 것과 해결 방법 기록 (다음에 새 컴퓨터를 세팅할 때 내가 읽을 글)

## 더 깊이

- `pip freeze > requirements.lock`으로 **모든** 패키지의 정확한 버전을 뽑아 보세요. `requirements.txt`와 무엇이 다른가요? 왜 두 파일이 필요할까요? (35단원 배포에서 다시 만납니다)
- `uv`, `poetry` 같은 도구가 무엇을 더 해 주는지 한 문단으로 정리해 보세요. 지금은 쓰지 않습니다.
