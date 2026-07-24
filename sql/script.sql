
CREATE TABLE IF NOT EXISTS portal_inicio_sesion (
    correo TEXT PRIMARY KEY,
    contrasena TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS administrador (
    id_admin INTEGER PRIMARY KEY AUTOINCREMENT,
    correo TEXT NOT NULL,
    contrasena TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS padres (
    id_padre INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    primer_apellido TEXT,
    telefono TEXT,
    correo TEXT REFERENCES portal_inicio_sesion(correo)
);

CREATE TABLE IF NOT EXISTS docente (
    id_docente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    clave_docente TEXT,
    correo TEXT REFERENCES portal_inicio_sesion(correo),
    id_admin INTEGER REFERENCES administrador(id_admin)
);

CREATE TABLE IF NOT EXISTS infante (
    id_infante INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    primer_apellido TEXT,
    segundo_apellido TEXT,
    edad INTEGER,
    tipo_de_condicion TEXT,
    id_padre INTEGER REFERENCES padres(id_padre),
    id_docente INTEGER REFERENCES docente(id_docente)
);

CREATE TABLE IF NOT EXISTS cuestionario (
    id_quiz INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    id_infante INTEGER REFERENCES infante(id_infante)
);

CREATE TABLE IF NOT EXISTS pregunta (
    id_pregunta INTEGER PRIMARY KEY AUTOINCREMENT,
    id_quiz INTEGER REFERENCES cuestionario(id_quiz),
    texto TEXT,
    puntos INTEGER,
    respuesta TEXT
);

CREATE TABLE IF NOT EXISTS resultado (
    id_resultado INTEGER PRIMARY KEY AUTOINCREMENT,
    id_quiz INTEGER REFERENCES cuestionario(id_quiz),
    id_infante INTEGER REFERENCES infante(id_infante),
    puntaje INTEGER,
    fecha TEXT,
    numero_de_especialista TEXT,
    nivel_riesgo TEXT
);

CREATE TABLE IF NOT EXISTS estrategias_didacticas (
    id_estrategia INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    objetivo TEXT,
    paso_a_paso TEXT,
    id_admin INTEGER REFERENCES administrador(id_admin)
);

CREATE TABLE IF NOT EXISTS consulta (
    id_docente INTEGER REFERENCES docente(id_docente),
    id_estrategia INTEGER REFERENCES estrategias_didacticas(id_estrategia),
    PRIMARY KEY (id_docente, id_estrategia)
);

CREATE TABLE IF NOT EXISTS actividad_asignada (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_docente INTEGER REFERENCES docente(id_docente),
    id_infante INTEGER REFERENCES infante(id_infante),
    descripcion TEXT,
    fecha_asignacion TEXT
);


INSERT INTO administrador (correo, contrasena) VALUES ('admin@conafe.gob.mx', '1234');

INSERT INTO docente (nombre, clave_docente, correo, id_admin)
VALUES ('Prof. Ana', 'CNF-1024', 'ana.martinez@conafe.gob.mx', 1);

INSERT INTO infante (nombre, primer_apellido, segundo_apellido, edad, tipo_de_condicion, id_docente) VALUES
    ('Juan', 'Pérez', 'López', 7, 'Autismo (TEA)', 1),
    ('Sofía', 'Ramírez', 'Díaz', 8, 'Autismo (TEA)', 1),
    ('Luis', 'Hernández', 'Cruz', 6, 'Autismo (TEA)', 1);

INSERT INTO estrategias_didacticas (titulo, objetivo, paso_a_paso, id_admin) VALUES
    ('Conteo con material concreto', 'Reforzar el conteo del 1 al 10', '1. Presentar fichas...', 1),
    ('Secuencias con pictogramas', 'Anticipar cambios de actividad', '1. Mostrar la secuencia visual...', 1),
    ('Rutina visual del día', 'Reducir ansiedad ante cambios', '1. Colocar el pizarrón de rutina...', 1);

INSERT INTO actividad_asignada (id_docente, id_infante, descripcion, fecha_asignacion) VALUES
    (1, 1, 'Actividad de conteo', DATE('now')),
    (1, 2, 'Rutina visual', DATE('now'));