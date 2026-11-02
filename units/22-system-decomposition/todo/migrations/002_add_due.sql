-- 12단원: 마감일
ALTER TABLE tasks ADD COLUMN due TEXT;
CREATE INDEX idx_tasks_due ON tasks(due);
