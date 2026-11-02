-- 14단원: 감사 로그와 전문 검색(FTS5)
CREATE TABLE audit_log (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    at      TEXT NOT NULL,
    action  TEXT NOT NULL,
    task_id INTEGER,
    detail  TEXT NOT NULL DEFAULT ''
);
CREATE VIRTUAL TABLE tasks_fts USING fts5(title, content='tasks', content_rowid='id');
CREATE TRIGGER tasks_ai AFTER INSERT ON tasks BEGIN
    INSERT INTO tasks_fts(rowid, title) VALUES (new.id, new.title);
END;
CREATE TRIGGER tasks_ad AFTER DELETE ON tasks BEGIN
    INSERT INTO tasks_fts(tasks_fts, rowid, title) VALUES ('delete', old.id, old.title);
END;
CREATE TRIGGER tasks_au AFTER UPDATE OF title ON tasks BEGIN
    INSERT INTO tasks_fts(tasks_fts, rowid, title) VALUES ('delete', old.id, old.title);
    INSERT INTO tasks_fts(rowid, title) VALUES (new.id, new.title);
END;
