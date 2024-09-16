-- Using postgresql

-- SYMBOLS REGION
-- symbols
-- Each row is a symbolic object in the text
CREATE TABLE IF NOT EXISTS "characters"(
    id BIGSERIAL PRIMARY KEY,
    text_ref REFERENCES texts(id) NOT NULL,
    pos_x INTEGER NOT NULL,
    pos_y INTEGER,
    pos_recto BOOLEAN,
    folio INTEGER,
    UNIQUE (text_ref, pos_x, pos_y, pos_recto, folio)
)

CREATE TABLE IF NOT EXISTS "markups"(
    id BIGSERIAL PRIMARY KEY,
    markup_class REFERENCES markup_types(id),
    creator REFERENCES users(id),
    -- Linguistic / textual
    has_language_of REFERENCES languages(id), -- P72
    has_style REFERENCES styles(id), -- TXP12
    employs_script REFERENCES scripts(id), --TXP16
    -- People. Derived from PASE and other sources
    was_written_by REFERENCES people(id), --TXP5
    grantor REFERENCES people(id), --P23
    grantee REFERENCES people(id), --P22
    former_title_holder REFERENCES people(id), --P23
    doc_witness REFERENCES people(id), --P11
    mentioned_person REFERENCES people(id), --P67
    -- Non-boundary locations
    took_place_at REFERENCES locations(id), --P7, aka promulgation
    transfers_title_to_place REFERENCES locations(id), --P24
    refers_to_location REFERENCES locations(id), --P67
    -- Boundary instructions
    boundary_instruction REFERENCES boundary_vertices(id),
    -- Transferible rights
    transfers_title_to_right REFERENCES rights(id)
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