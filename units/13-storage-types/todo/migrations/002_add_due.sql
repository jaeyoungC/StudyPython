-- 002: 마감일(due) 열 추가. ISO 날짜 문자열 "YYYY-MM-DD" 를 저장한다. 없으면 NULL.
-- ALTER TABLE ... ADD COLUMN 은 기존 행을 다시 쓰지 않는다(새 열은 NULL/DEFAULT 로 읽힌다). 10만 건이어도 즉시 끝난다.
ALTER TABLE tasks ADD COLUMN due TEXT;
