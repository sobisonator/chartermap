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
    markup_class REFERENCES markup_classes(id),
    creator REFERENCES users(id),
    -- Linguistic / textual
    has_language_of REFERENCES languages(id), -- P72
    has_style REFERENCES styles(id), -- TXP12
    employs_script REFERENCES scripts(id), --TXP16
    -- People. Derived from PASE and other sources
    was_written_by REFERENCES people(id), --TXP5
    grantor REFERENCES people(id), --P23
    beneficiary REFERENCES people(id), --P22
    former_title_holder REFERENCES people(id), --P23
    doc_witness REFERENCES people(id), --P11
    mentioned_person REFERENCES people(id), --P67
    -- Non-boundary locations
    took_place_at REFERENCES locations(id), --P7, aka promulgation
    transfers_title_to_place REFERENCES locations(id), --P24
    refers_to_location REFERENCES locations(id), --P67
    -- Boundary instructions
    boundary_instruction REFERENCES boundary_instructions(id),
    -- Transferible rights
    transfers_title_to_right REFERENCES rights(id),
    -- Diplomatic phrases
    diplomatic_form REFERENCES diplomatic_forms(id)
)

CREATE TABLE IF NOT EXISTS "markup_conversations"(
    id SERIAL PRIMARY KEY,
    markup REFERENCES markups(id),
)

CREATE TABLE IF NOT EXISTS "markup_comments"(
    id BIGSERIAL PRIMARY KEY,
    creator REFERENCES users(id) NOT NULL,
    created DATETIME NOT NULL, -- Determines the sequence of comments
    markup_conversation REFERENCES markup_conversations(id) NOT NULL,
    contents VARCHAR
)

CREATE TABLE IF NOT EXISTS "markup_classes"(
    id SERIAL PRIMARY KEY,
    label VARCHAR NOT NULL
)

CREATE TABLE IF NOT EXISTS "users"(
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL
)

CREATE TABLE IF NOT EXISTS "langauges"(
    id SERIAL PRIMARY KEY,
    label VARCHAR NOT NULL
)

CREATE TABLE IF NOT EXISTS "styles"(
    id SERIAL PRIMARY KEY,
    label VARCHAR NOT NULL,
    class REFERENCES style_classes(id),
    descr VARCHAR
)

CREATE TABLE IF NOT EXISTS "style_classes"(
    id SERIAL PRIMARY KEY,
    label VARCHAR NOT NULL
)

CREATE TABLE IF NOT EXISTS "scripts"(
    id SERIAL PRIMARY KEY,
    label VARCHAR NOT NULL,
    descr VARCHAR NOT NULL
)

CREATE TABLE IF NOT EXISTS "people"(
    id SERIAL PRIMARY KEY,
    pase_id VARCHAR,
    backup_id VARCHAR,
    scope VARCHAR
)

CREATE TABLE IF NOT EXISTS "locations"(
    id SERIAL PRIMARY KEY
    coordinates POINT NOT NULL
)

CREATE TABLE IF NOT EXISTS "boundary_instructions"(
    id SERIAL PRIMARY KEY,
    -- next_instruction implicitly links up points and paths into a super-path
    next_instruction REFERENCES boundary_instructions(id),
    boundary_vertex REFERENCES boundary_vertices(id),
    boundary_path REFERENCES boundary_paths(id),
    -- Only one of vertex or path can be used
    CONSTRAINT CHECK (boundary_vertex IS NULL <> boundary_path IS NULL)
)

CREATE TABLE IF NOT EXISTS "boundary_vertices"(
    id SERIAL PRIMARY KEY,
    coordinates POINT NOT NULL,
    accuracy INTEGER
)

CREATE TABLE IF NOT EXISTS "boundary_paths"(
    id SERIAL PRIMARY KEY,
    coordinates PATH NOT NULL
    accuracy INTEGER
)

CREATE TABLE IF NOT EXISTS "rights"(
    id SERIAL PRIMARY KEY,
    label VARCHAR NOT NULL,
    descr VARCHAR NOT NULL
)

CREATE TABLE IF NOT EXISTS "diplomatic_forms"(
    id SERIAL PRIMARY KEY,
    ideal_form VARCHAR NOT NULL,
    class REFERENCES diplomatic_form_classes(id)
)

CREATE TABLE IF NOT EXISTS "diplomatic_form_classes"(
    id SERIAL PRIMARY KEY,
    label VARCHAR NOT NULL,
    descr VARCHAR NOT NULL
)