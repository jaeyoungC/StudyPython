"""34단원 테스트 뼈대. 실행: pytest units/34-ci-cd

CI 설정 파일도 코드입니다. 깨진 YAML, 빠진 단계, 잘못된 브랜치 이름을 로컬에서 먼저 잡습니다.
pip install pyyaml 이 필요합니다. 검사 대상은 저장소 루트의 .github/workflows/ci.yml (ci.yml.example 을 복사한 것).
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def load_workflow() -> dict:
    """yaml.safe_load 로 읽는다. 주의: YAML 은 키 `on` 을 True 로 파싱할 수 있다(yaml 1.1). 그 점을 테스트에서 다룬다."""
    pytest.fail("아직 구현하지 않음")


def test_workflow_file_exists_and_parses():
    """.github/workflows/ci.yml 이 있고 YAML 로 파싱된다."""
    pytest.fail("아직 구현하지 않음")


def test_workflow_runs_on_pull_request_and_main_push():
    """on 에 pull_request 가 있고 push.branches 에 main 이 있다."""
    pytest.fail("아직 구현하지 않음")


def test_test_job_has_python_matrix_with_two_versions():
    """jobs.test.strategy.matrix.python-version 에 "3.12" 와 "3.13" 이 들어 있다."""
    pytest.fail("아직 구현하지 않음")


def test_test_job_depends_on_lint():
    """jobs.test.needs 가 lint 를 포함한다 (린트 실패 시 테스트를 건너뛴다)."""
    pytest.fail("아직 구현하지 않음")


def test_lint_job_runs_ruff_bandit_and_pip_audit():
    """lint job 의 run 단계 문자열들을 합쳤을 때 ruff, bandit, pip-audit 이 모두 들어 있다."""
    pytest.fail("아직 구현하지 않음")


def test_no_real_secret_values_in_workflow():
    """워크플로 파일 텍스트에 'sk-live', 'password=' 같은 패턴이 없고, 비밀값은 ${{ secrets.* }} 또는 가짜 표시 값만 쓴다."""
    pytest.fail("아직 구현하지 않음")


def test_permissions_are_read_only():
    """최상위 permissions.contents 가 read 이다 (30단원 최소 권한)."""
    pytest.fail("아직 구현하지 않음")


def test_pip_cache_is_enabled_in_setup_python():
    """모든 setup-python 단계에 with.cache: pip 이 있다 (캐시 없는 CI 는 매번 전체 설치)."""
    pytest.fail("아직 구현하지 않음")
