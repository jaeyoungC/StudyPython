"""`python -m todo` 로 실행될 때의 진입점. sys.exit 는 여기 한 곳에서만 부른다."""

import sys

from todo.cli import main

if __name__ == "__main__":
    sys.exit(main())
