-- Using postgresql

-- Characters
-- Each row is a character
CREATE TABLE IF NOT EXISTS "characters"(
    char_uid INTEGER PRIMARY KEY,
    text_id VARCHAR NOT NULL,
    pos INTEGER NOT NULL,
    UNIQUE (text_id, pos)
)