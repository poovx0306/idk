CREATE TABLE IF NOT EXISTS actividad_postcrisis (
    id_actividad INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    duracion_min INTEGER,
    pasos TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS actividad_postcrisis_realizada (
    id_realizada INTEGER PRIMARY KEY AUTOINCREMENT,
    id_infante INTEGER NOT NULL,
    id_actividad INTEGER NOT NULL,
    fecha TEXT NOT NULL
);

INSERT INTO actividad_postcrisis (titulo, descripcion, duracion_min, pasos) VALUES
('Rincón de calma', 'Llevar al niño a un espacio silencioso y conocido, sin exigir que hable ni se mueva.', 10,
'1. Baja la luz y el ruido.
2. Ofrece su objeto de calma favorito.
3. Quédate cerca en silencio, sin presionar.
4. Di frases cortas: "Estoy aquí contigo".'),
('Presión profunda', 'Un abrazo firme o una manta pesada puede ayudar a regular el sistema nervioso.', 5,
'1. Verifica que a tu hijo le guste el contacto físico.
2. Ofrece un abrazo firme y sostenido, o una manta/cojín pesado.
3. Mantenlo el tiempo que el niño lo pida.'),
('Vuelta gradual a la rutina', 'Retomar la actividad normal poco a poco, sin forzar.', 15,
'1. Espera a que el niño se vea más tranquilo.
2. Ofrece elegir entre 2 actividades simples.
3. Retoma la rutina normal sin mencionar la crisis.');