-- ============================================================
-- CONAAP · Retroalimentación del docente por tema
--
-- criterio_tema             -> los checkboxes que define el administrador
-- retroalimentacion         -> una por alumno + tema + fecha
-- retroalimentacion_criterio-> qué criterios logró y cuáles no
-- ============================================================

CREATE TABLE IF NOT EXISTS criterio_tema (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tema INTEGER NOT NULL,
    texto TEXT NOT NULL,
    FOREIGN KEY (id_tema) REFERENCES temas(id)
);

CREATE TABLE IF NOT EXISTS retroalimentacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tema INTEGER NOT NULL,
    id_infante INTEGER NOT NULL,
    id_docente INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (id_tema) REFERENCES temas(id),
    FOREIGN KEY (id_infante) REFERENCES infantes(id_infante),
    FOREIGN KEY (id_docente) REFERENCES docente(id_docente)
);

CREATE TABLE IF NOT EXISTS retroalimentacion_criterio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_retroalimentacion INTEGER NOT NULL,
    id_criterio INTEGER NOT NULL,
    logrado INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (id_retroalimentacion) REFERENCES retroalimentacion(id),
    FOREIGN KEY (id_criterio) REFERENCES criterio_tema(id)
);


-- ============================================================
-- Criterios iniciales para los temas de CONAFE
-- (el administrador puede agregar y quitar más desde el panel)
-- ============================================================

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Eligió su tema de forma autónoma entre las opciones visuales' FROM temas WHERE titulo = 'Cuentos y leyendas tradicionales de la comunidad';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Identificó al personaje principal del cuento' FROM temas WHERE titulo = 'Cuentos y leyendas tradicionales de la comunidad';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Ordenó las escenas en la secuencia correcta (inicio, desarrollo, final)' FROM temas WHERE titulo = 'Cuentos y leyendas tradicionales de la comunidad';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Mantuvo la atención durante la lectura guiada' FROM temas WHERE titulo = 'Cuentos y leyendas tradicionales de la comunidad';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Clasificó correctamente qué come el animal' FROM temas WHERE titulo = 'Textos informativos sobre animales de la comunidad';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Clasificó correctamente dónde vive el animal' FROM temas WHERE titulo = 'Textos informativos sobre animales de la comunidad';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Descartó las imágenes que no correspondían al animal' FROM temas WHERE titulo = 'Textos informativos sobre animales de la comunidad';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Siguió los pasos del instructivo en orden' FROM temas WHERE titulo = 'Carteles e instructivos de la vida cotidiana';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Reorganizó las fotos en la secuencia correcta sin ayuda' FROM temas WHERE titulo = 'Carteles e instructivos de la vida cotidiana';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Ejecutó la actividad de forma autónoma' FROM temas WHERE titulo = 'Carteles e instructivos de la vida cotidiana';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Logró la correspondencia uno a uno al contar' FROM temas WHERE titulo = 'Conteo y colecciones del entorno';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Relacionó la cantidad con la tarjeta numérica correcta' FROM temas WHERE titulo = 'Conteo y colecciones del entorno';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Contó hasta 5 sin apoyo del tutor' FROM temas WHERE titulo = 'Conteo y colecciones del entorno';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Resolvió correctamente las sumas' FROM temas WHERE titulo = 'Operaciones básicas: suma y resta';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Resolvió correctamente las restas' FROM temas WHERE titulo = 'Operaciones básicas: suma y resta';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Comprendió sumar como juntar y restar como quitar' FROM temas WHERE titulo = 'Operaciones básicas: suma y resta';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Manipuló el material concreto sin frustrarse' FROM temas WHERE titulo = 'Operaciones básicas: suma y resta';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Separó la barra en dos partes iguales' FROM temas WHERE titulo = 'Fracciones y repartos equitativos';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Distinguió la mitad exacta de un reparto desigual' FROM temas WHERE titulo = 'Fracciones y repartos equitativos';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Usó el vocabulario mitad o partes iguales' FROM temas WHERE titulo = 'Fracciones y repartos equitativos';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Clasificó los objetos según su forma geométrica' FROM temas WHERE titulo = 'Formas geométricas y cuerpos en la naturaleza';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Emparejó un objeto nuevo con su figura correspondiente' FROM temas WHERE titulo = 'Formas geométricas y cuerpos en la naturaleza';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Reconoció los bordes de las figuras al tacto' FROM temas WHERE titulo = 'Formas geométricas y cuerpos en la naturaleza';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Identificó cuál objeto es más pesado' FROM temas WHERE titulo = 'Medición, pesos y longitudes';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Identificó cuál tira es más larga' FROM temas WHERE titulo = 'Medición, pesos y longitudes';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Usó correctamente la balanza o la cinta de medir' FROM temas WHERE titulo = 'Medición, pesos y longitudes';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Colocó los órganos en la posición correcta de la silueta' FROM temas WHERE titulo = 'El cuerpo humano y los órganos vitales';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Asoció cada órgano con su función' FROM temas WHERE titulo = 'El cuerpo humano y los órganos vitales';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Nombró al menos tres órganos vitales' FROM temas WHERE titulo = 'El cuerpo humano y los órganos vitales';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Identificó las cuatro partes de la planta' FROM temas WHERE titulo = 'Las plantas y el cuidado del medio ambiente';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Ensambló la planta en el orden correcto' FROM temas WHERE titulo = 'Las plantas y el cuidado del medio ambiente';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Toleró el contacto con el material natural' FROM temas WHERE titulo = 'Las plantas y el cuidado del medio ambiente';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Ubicó los puntos clave de la comunidad en la maqueta' FROM temas WHERE titulo = 'Mi comunidad, croquis y trayectos';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Trazó el recorrido de su casa a la escuela' FROM temas WHERE titulo = 'Mi comunidad, croquis y trayectos';
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Realizó un recorrido nuevo de forma autónoma' FROM temas WHERE titulo = 'Mi comunidad, croquis y trayectos';


-- Verificación
SELECT t.titulo, COUNT(c.id) AS criterios
FROM temas t LEFT JOIN criterio_tema c ON c.id_tema = t.id
GROUP BY t.id ORDER BY t.id;