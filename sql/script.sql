<<<<<<< HEAD
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario  INTEGER PRIMARY KEY AUTOINCREMENT,
    correo      TEXT NOT NULL UNIQUE,
    contrasena  TEXT NOT NULL,
    rol         TEXT NOT NULL,
    nombre      TEXT NOT NULL
=======

CREATE TABLE IF NOT EXISTS portal_inicio_sesion (
    correo TEXT PRIMARY KEY,
    contrasena TEXT NOT NULL
>>>>>>> origin/main
);


CREATE TABLE IF NOT EXISTS administrador (
    id_admin    INTEGER PRIMARY KEY AUTOINCREMENT,
    correo      TEXT NOT NULL,
    contrasena  TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS docente (
    id_docente     INTEGER PRIMARY KEY AUTOINCREMENT,
    clave_docente  TEXT NOT NULL,
    nombre         TEXT NOT NULL,
    id_admin       INTEGER NOT NULL REFERENCES administrador(id_admin)
);


CREATE TABLE IF NOT EXISTS preguntas (
    id_pregunta  INTEGER PRIMARY KEY AUTOINCREMENT,
    texto        TEXT NOT NULL,
    puntos       INTEGER NOT NULL,
    respuesta    TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS cuestionario (
    id_cuestionario  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pregunta      INTEGER NOT NULL REFERENCES preguntas(id_pregunta),
    id_admin         INTEGER NOT NULL REFERENCES administrador(id_admin)
);


CREATE TABLE IF NOT EXISTS estrategias_didacticas (
    id_estrategia  INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo         TEXT NOT NULL,
    objetivo       TEXT NOT NULL,
    paso_a_paso    TEXT NOT NULL,
    id_admin1      INTEGER NOT NULL REFERENCES administrador(id_admin),
    id_docente2    INTEGER NOT NULL REFERENCES docente(id_docente)
);


CREATE TABLE IF NOT EXISTS padres (
    id_padres  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre     TEXT NOT NULL,
    telefono   TEXT NOT NULL
);

<<<<<<< HEAD

CREATE TABLE IF NOT EXISTS portal_inicio_sesion (
    correo      TEXT PRIMARY KEY,
    contrasena  TEXT NOT NULL,
    id_padres   INTEGER NOT NULL REFERENCES padres(id_padres)
=======
CREATE TABLE IF NOT EXISTS actividad_asignada (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_docente INTEGER REFERENCES docente(id_docente),
    id_infante INTEGER REFERENCES infante(id_infante),
    descripcion TEXT,
    fecha_asignacion TEXT
>>>>>>> origin/main
);


CREATE TABLE IF NOT EXISTS infantes (
    id_infante   INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL,
    edad         INTEGER NOT NULL,
    id_docente1  INTEGER NOT NULL REFERENCES docente(id_docente),
    id_padres    INTEGER NOT NULL REFERENCES padres(id_padres)
);


CREATE TABLE IF NOT EXISTS resultados (
    id_resultado            INTEGER PRIMARY KEY AUTOINCREMENT,
    puntaje                 INTEGER NOT NULL,
    fecha                   TEXT NOT NULL,
    nivel_riesgo            TEXT NOT NULL,
    numero_de_especialista  TEXT NOT NULL,
    id_infante1             INTEGER NOT NULL REFERENCES infantes(id_infante)
);