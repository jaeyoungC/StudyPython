"""`python -m todo` 로 실행될 때의 진입점."""

import sys

from .cli import main

sys.exit(main())
