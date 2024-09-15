-- Using postgresql

-- SYMBOLS REGION
-- symbols
-- Each row is a symbolic object in the text
CREATE TABLE IF NOT EXISTS "glpyhs"(
    char_uid INTEGER PRIMARY KEY,
    text_ref VARCHAR NOT NULL, -- Does this want to reference texts outside of the system, in a 3rd party digital archive?
    pos INTEGER NOT NULL,
    UNIQUE (text_id, pos)
)

-- MARKUPS REGION
-- Every markup should denote a property-entity relationship in the text
-- available combinations are
-- P72 Has language : E56 Language
-- P76 Refers to : [person, place]
-- 

-- markups
-- Lists the markups created
CREATE TABLE IF NOT EXISTS "markups"(
    markup_uid INTEGER PRIMARY KEY,
    markup_notes VARCHAR
    markup_type INTEGER NOT NULL REFERENCES markup_types(markup_type_uid)   
)

-- markup_tags
-- Connects markups with tags
CREATE TABLE IF NOT EXISTS "markup_tags"(
    markup_tag_uid INTEGER PRIMARY KEY,
    markup_ref INTEGER REFERENCES markups(markup_uid),
    tag_ref VARCHAR NOT NULL REFERENCES tags(tag_uid)
)

-- markup_regions
-- Connects a markup to all of the symbols within the "highlight" region.
CREATE TABLE IF NOT EXISTS "markup_regions"(
    markup_region_uid INTEGER PRIMARY KEY,
    markup_ref INTEGER REFERENCES markups(markup_uid),
    char_ref INTEGER NOT NULL REFERENCES symbols(symbol_uid),
)

-- TAGS REGION
-- tags
-- Defines the tags available to link to the text
CREATE TABLE IF NOT EXISTS "tags"(
    tag_uid INTEGER PRIMARY KEY,
    tag_text VARCHAR
)

-- ENTITY TYPES REGION
-- markup_types
-- Defines the types of information that a markup can denote
-- ... (e.g. "person", "place", "script", "hand", "language") available
CREATE TABLE IF NOT EXISTS "markup_types"(
    markup_type_uid INTEGER PRIMARY KEY
)