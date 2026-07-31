CREATE TABLE IF NOT EXISTS racha_infante (
    id_infante INTEGER PRIMARY KEY,
    racha_actual INTEGER DEFAULT 0,
    racha_maxima INTEGER DEFAULT 0,
    ultima_semana_iso TEXT
);