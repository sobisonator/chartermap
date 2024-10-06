-- Using postgresql

-- CHARACTERS REGION
-- symbols
-- Each row is a symbolic object in the text
CREATE TABLE IF NOT EXISTS "characters"(
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR NOT NULL,
    text_ref INTEGER REFERENCES texts(id) NOT NULL,
    pos_x INTEGER NOT NULL,
    pos_y INTEGER,
    pos_recto BOOLEAN,
    folio INTEGER,
    UNIQUE (text_ref, pos_x, pos_y, pos_recto, folio)
);

CREATE TABLE IF NOT EXISTS "texts"(
    id SERIAL PRIMARY KEY,
    label VARCHAR NOT NULL,
    manuscript URL -- Should refer to an external record of a manuscript
);

    CREATE TABLE IF NOT EXISTS "markups"(
        id BIGSERIAL PRIMARY KEY,
        markup_class INTEGER REFERENCES markup_classes(id),
        creator INTEGER REFERENCES users(id),
        -- Linguistic / textual
        has_language_of INTEGER REFERENCES languages(id), -- P72
        has_style INTEGER REFERENCES styles(id), -- TXP12
        employs_script INTEGER REFERENCES scripts(id), --TXP16
        -- People. Derived from PASE and other sources
        was_written_by INTEGER REFERENCES people(id), --TXP5
        grantor INTEGER REFERENCES people(id), --P23
        beneficiary INTEGER REFERENCES people(id), --P22
        former_title_holder INTEGER REFERENCES people(id), --P23
        doc_witness INTEGER REFERENCES people(id), --P11
        mentioned_person INTEGER REFERENCES people(id), --P67
        -- Non-boundary locations
        took_place_at INTEGER REFERENCES locations(id), --P7, aka promulgation
        transfers_title_to_place INTEGER REFERENCES locations(id), --P24
        refers_to_location INTEGER REFERENCES locations(id), --P67
        -- Boundary instructions
        boundary_instruction INTEGER REFERENCES boundary_instructions(id),
        -- Transferible rights
        transfers_title_to_right INTEGER REFERENCES rights(id),
        -- Diplomatic phrases
        diplomatic_form INTEGER REFERENCES diplomatic_forms(id)
    );

CREATE TABLE IF NOT EXISTS "markup_associations"(
    id BIGSERIAL PRIMARY KEY,
    markup INTEGER REFERENCES markups(id),
    character_id INTEGER REFERENCES characters(id)
);

    CREATE TABLE IF NOT EXISTS "markup_conversations"(
        id SERIAL PRIMARY KEY,
        markup REFERENCES markups(id),
    )

    CREATE TABLE IF NOT EXISTS "markup_comments"(
        id BIGSERIAL PRIMARY KEY,
        creator INTEGER REFERENCES users(id) NOT NULL,
        created DATETIME NOT NULL, -- Determines the sequence of comments
        markup_conversation INTEGER REFERENCES markup_conversations(id) NOT NULL,
        contents VARCHAR
    );

    CREATE TABLE IF NOT EXISTS "markup_classes"(
        id SERIAL PRIMARY KEY,
        label VARCHAR NOT NULL
    );

    CREATE TABLE IF NOT EXISTS "users"(
        id SERIAL PRIMARY KEY,
        username VARCHAR NOT NULL
    );

    CREATE TABLE IF NOT EXISTS "langauges"(
        id SERIAL PRIMARY KEY,
        label VARCHAR NOT NULL
    );

    CREATE TABLE IF NOT EXISTS "styles"(
        id SERIAL PRIMARY KEY,
        label VARCHAR NOT NULL,
        class INTEGER REFERENCES style_classes(id),
        descr VARCHAR
    );

    CREATE TABLE IF NOT EXISTS "style_classes"(
        id SERIAL PRIMARY KEY,
        label VARCHAR NOT NULL
    );

    CREATE TABLE IF NOT EXISTS "scripts"(
        id SERIAL PRIMARY KEY,
        label VARCHAR NOT NULL,
        descr VARCHAR NOT NULL
    );

    CREATE TABLE IF NOT EXISTS "people"(
        id SERIAL PRIMARY KEY,
        pase_id VARCHAR,
        backup_id VARCHAR,
        scope VARCHAR
    );

    CREATE TABLE IF NOT EXISTS "locations"(
        id SERIAL PRIMARY KEY,
        coordinates POINT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS "boundary_instructions"(
        id SERIAL PRIMARY KEY,
        -- next_instruction implicitly links up points and paths into a super-path
        next_instruction INTEGER REFERENCES boundary_instructions(id),
        boundary_vertex INTEGER REFERENCES boundary_vertices(id),
        boundary_path INTEGER REFERENCES boundary_paths(id),
        -- Only one of vertex or path can be used
        CHECK(boundary_vertex IS NULL <> boundary_path IS NULL)
    );

    CREATE TABLE IF NOT EXISTS "boundary_vertices"(
        id SERIAL PRIMARY KEY,
        coordinates POINT NOT NULL,
        accuracy INTEGER
    );

    CREATE TABLE IF NOT EXISTS "boundary_paths"(
        id SERIAL PRIMARY KEY,
        coordinates PATH NOT NULL,
        accuracy INTEGER
    );

    CREATE TABLE IF NOT EXISTS "rights"(
        id SERIAL PRIMARY KEY,
        label VARCHAR NOT NULL,
        descr VARCHAR NOT NULL
    );

    CREATE TABLE IF NOT EXISTS "diplomatic_forms"(
        id SERIAL PRIMARY KEY,
        ideal_form VARCHAR NOT NULL,
        class INTEGER REFERENCES diplomatic_form_classes(id)
    );

    CREATE TABLE IF NOT EXISTS "diplomatic_form_classes"(
        id SERIAL PRIMARY KEY,
        label VARCHAR NOT NULL,
        descr VARCHAR NOT NULL
    )