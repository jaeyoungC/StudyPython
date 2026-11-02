"""12단원: 백업과 복구.

SQLite 파일을 그냥 복사(`shutil.copy`)하면 안 되는 이유: 다른 연결이 쓰는 중이면 반쯤 쓰인 파일이 복사된다.
`Connection.backup(dest)` 는 DB 가 사용 중이어도 **일관된 시점의 사본**을 만든다 (온라인 백업 API).
`:memory:` DB 도 백업할 수 있어서 테스트하기 쉽다.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def backup_to(conn: sqlite3.Connection, path: Path) -> Path:
    """conn 의 내용을 path 파일에 백업하고 path 를 돌려준다. 부모 폴더가 없으면 만든다.

    힌트: 대상 파일에 연결을 열고 `conn.backup(대상연결)` 을 부른 뒤 대상 연결을 닫는다 (try/finally).
    """
    # TODO
    raise NotImplementedError


def restore_from(path: Path, conn: sqlite3.Connection) -> None:
    """path 백업 파일의 내용으로 conn 의 DB 를 **통째로 교체**한다. conn 에 있던 데이터는 사라진다.

    힌트: 방향만 반대다 — 백업 파일에 연결을 열고 `백업연결.backup(conn)`.
    """
    # TODO
    raise NotImplementedError
