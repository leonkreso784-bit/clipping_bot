-- Baza stanja (dizajn §8). Imena tablica i statusa su na hrvatskom jer ih Leon vidi.
-- Izvršava se pri svakom pokretanju; sve naredbe moraju biti idempotentne.

CREATE TABLE IF NOT EXISTS migracija (
    verzija INTEGER PRIMARY KEY,
    vrijeme TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kampanja (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    kreator TEXT NOT NULL,
    profil_json TEXT NOT NULL,
    azurirano TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS izvor (
    id INTEGER PRIMARY KEY,
    kampanja_id INTEGER NOT NULL REFERENCES kampanja(id),
    url TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    putanja TEXT NOT NULL,
    zapis_prava TEXT NOT NULL,
    dodano TEXT NOT NULL,
    UNIQUE (kampanja_id, url)
);

CREATE TABLE IF NOT EXISTS posao (
    id TEXT PRIMARY KEY,
    izvor_id INTEGER NOT NULL REFERENCES izvor(id),
    izvor_sha256 TEXT NOT NULL,
    platforme_json TEXT NOT NULL,
    stvoreno TEXT NOT NULL,
    zavrseno TEXT
);

CREATE TABLE IF NOT EXISTS korak (
    posao_id TEXT NOT NULL REFERENCES posao(id),
    korak TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pocet', 'gotov', 'greska')),
    poruka TEXT NOT NULL DEFAULT '',
    vrijeme TEXT NOT NULL,
    PRIMARY KEY (posao_id, korak)
);

CREATE TABLE IF NOT EXISTS isjecak (
    id INTEGER PRIMARY KEY,
    posao_id TEXT NOT NULL REFERENCES posao(id),
    redni INTEGER NOT NULL,
    start_word INTEGER NOT NULL,
    end_word INTEGER NOT NULL,
    start_s REAL NOT NULL,
    end_s REAL NOT NULL,
    naslov TEXT NOT NULL,
    udica TEXT NOT NULL,
    ocjena INTEGER NOT NULL,
    razlog TEXT NOT NULL DEFAULT '',
    opis TEXT NOT NULL DEFAULT '',
    stil TEXT NOT NULL,
    putanja TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN (
        'izrezan', 'provjeren', 'odobren', 'izbacen',
        'zakazan', 'objavljen', 'prijavljen', 'placen'
    )),
    qa_ok INTEGER,
    qa_nalazi_json TEXT NOT NULL DEFAULT '[]',
    pregled_ocjena INTEGER,
    pregled_problemi_json TEXT NOT NULL DEFAULT '[]',
    UNIQUE (posao_id, redni)
);

CREATE TABLE IF NOT EXISTS objava (
    id INTEGER PRIMARY KEY,
    isjecak_id INTEGER NOT NULL REFERENCES isjecak(id),
    platforma TEXT NOT NULL,
    racun TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN (
        'ceka', 'zakazano', 'objavljeno', 'greska', 'rucno_ceka_url'
    )),
    url TEXT,
    vrijeme TEXT,
    UNIQUE (isjecak_id, platforma)
);

CREATE TABLE IF NOT EXISTS pregledi (
    objava_id INTEGER NOT NULL REFERENCES objava(id),
    datum TEXT NOT NULL,
    broj INTEGER NOT NULL,
    PRIMARY KEY (objava_id, datum)
);

CREATE TABLE IF NOT EXISTS isplata (
    id INTEGER PRIMARY KEY,
    kampanja_id INTEGER NOT NULL REFERENCES kampanja(id),
    iznos_usd REAL NOT NULL,
    datum TEXT NOT NULL,
    napomena TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS dogadjaj (
    id INTEGER PRIMARY KEY,
    posao_id TEXT,
    vrijeme TEXT NOT NULL,
    razina TEXT NOT NULL,
    poruka TEXT NOT NULL
);

INSERT OR IGNORE INTO migracija (verzija, vrijeme) VALUES (1, datetime('now'));
