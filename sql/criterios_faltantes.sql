-- ============================================================
-- CONAAP · Completar criterios de evaluación
--
-- Agrega criterios SOLO a los temas que no tienen ninguno.
-- Es seguro correrlo varias veces: si todos los temas ya
-- tienen criterios, no inserta nada.
-- ============================================================

-- Se congela aquí la lista de temas vacíos, para que los INSERT
-- de abajo no se pisen entre ellos.
CREATE TEMP TABLE temas_vacios AS
SELECT id, titulo FROM temas
WHERE id NOT IN (SELECT id_tema FROM criterio_tema);


-- ---------- Conteo con material concreto ----------
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Contó en voz alta moviendo cada objeto uno por uno'
FROM temas_vacios WHERE titulo = 'Conteo con material concreto';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Agrupó los objetos de 2 en 2 o de 5 en 5'
FROM temas_vacios WHERE titulo = 'Conteo con material concreto';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Registró el resultado escribiendo el número correcto'
FROM temas_vacios WHERE titulo = 'Conteo con material concreto';


-- ---------- Secuencias con pictogramas ----------
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Señaló el pictograma que faltaba en la secuencia'
FROM temas_vacios WHERE titulo = 'Secuencias con pictogramas';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Verbalizó la secuencia completa con apoyo del tutor'
FROM temas_vacios WHERE titulo = 'Secuencias con pictogramas';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Resolvió una secuencia nueva de mayor dificultad'
FROM temas_vacios WHERE titulo = 'Secuencias con pictogramas';


-- ---------- Rutina visual del día ----------
INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Identificó las actividades de su rutina en la agenda visual'
FROM temas_vacios WHERE titulo = 'Rutina visual del día';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Anticipó qué actividad seguía sin necesidad de preguntar'
FROM temas_vacios WHERE titulo = 'Rutina visual del día';

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Toleró un cambio en la rutina sin presentar crisis'
FROM temas_vacios WHERE titulo = 'Rutina visual del día';


-- ============================================================
-- Respaldo: cualquier otro tema vacío recibe los cuatro
-- criterios genéricos del proceso tutorial de CONAFE.
-- Esto cubre los temas que el administrador dé de alta después.
-- ============================================================

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Eligió el tema de forma autónoma entre las opciones visuales'
FROM temas_vacios
WHERE titulo NOT IN ('Conteo con material concreto',
                     'Secuencias con pictogramas',
                     'Rutina visual del día');

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Mantuvo la atención durante la explicación del tutor'
FROM temas_vacios
WHERE titulo NOT IN ('Conteo con material concreto',
                     'Secuencias con pictogramas',
                     'Rutina visual del día');

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Completó las actividades de comprensión con el material concreto'
FROM temas_vacios
WHERE titulo NOT IN ('Conteo con material concreto',
                     'Secuencias con pictogramas',
                     'Rutina visual del día');

INSERT INTO criterio_tema (id_tema, texto)
SELECT id, 'Demostró lo aprendido en la evaluación final'
FROM temas_vacios
WHERE titulo NOT IN ('Conteo con material concreto',
                     'Secuencias con pictogramas',
                     'Rutina visual del día');


DROP TABLE temas_vacios;


-- Verificación: ningún tema debe quedar en 0
SELECT t.id, t.titulo, COUNT(c.id) AS criterios
FROM temas t LEFT JOIN criterio_tema c ON c.id_tema = t.id
GROUP BY t.id ORDER BY criterios ASC, t.id;