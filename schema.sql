CREATE TABLE IF NOT EXISTS definitions (
    id INTEGER PRIMARY KEY,
    definition TEXT NOT NULL
);

-- auxiliary = 0 for haben, 1 for sein
-- seperable = 0 for false, 1 for true
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    auxiliary INTEGER,
    regular INTEGER NOT NULL,
    separable INTEGER,
    definition_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    gender_id INTEGER,
    FOREIGN KEY (definition_id) REFERENCES definitions(id),
    FOREIGN KEY (type_id)       REFERENCES types(id)
    FOREIGN KEY (gender_id)       REFERENCES genders(id)
);

CREATE TABLE IF NOT EXISTS conjugations (
    id INTEGER PRIMARY KEY,
    tense TEXT NOT NULL,
    pronoun TEXT,
    conjugation TEXT,
    word_id INTEGER NOT NULL,
    mood_id INTEGER NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words(id),
    UNIQUE(tense, pronoun, conjugation, mood_id, word_id)
);

-- number = 0 for plural, 1 for singular
CREATE TABLE IF NOT EXISTS declensions (
    id INTEGER PRIMARY KEY,
    nominative TEXT NOT NULL,
    genitive TEXT NOT NULL,
    dative TEXT NOT NULL,
    accusative TEXT NOT NULL,
    number INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words(id)
);

CREATE TABLE IF NOT EXISTS sentences (
    id INTEGER PRIMARY KEY,
    sentence TEXT NOT NULL,
    word_id INTEGER NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words(id)
);

CREATE TABLE IF NOT EXISTS types (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS moods (
    id INTEGER PRIMARY KEY,
    mood TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS genders (
    id INTEGER PRIMARY KEY,
    gender TEXT NOT NULL
);
