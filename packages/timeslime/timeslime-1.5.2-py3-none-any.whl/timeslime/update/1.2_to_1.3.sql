UPDATE timespans SET id = REPLACE(id, '-', '');
UPDATE settings SET id = REPLACE(id, '-', '');

ALTER TABLE settings ADD COLUMN created_at DATETIME;
ALTER TABLE settings ADD COLUMN updated_at DATETIME;
UPDATE settings SET created_at = DATETIME('now', 'unixepoch'), updated_at = DATETIME('now') WHERE created_at is NULL;

ALTER TABLE timespans ADD COLUMN created_at DATETIME;
ALTER TABLE timespans ADD COLUMN updated_at DATETIME;
UPDATE timespans SET created_at = DATETIME('now'), updated_at = DATETIME('now') WHERE created_at is NULL;