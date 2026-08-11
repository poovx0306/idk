-- ============================================================
-- CONAAP · Carga de temas del proceso de relación tutora 1 a 1 (CONAFE)
-- Adaptación para aprendientes con autismo (preescolar y primaria)
--
-- Tabla destino: temas
-- Estructura de paso_a_paso: las 4 etapas del diálogo tutorial
-- separadas por "|" (Elección | Explicación | Actividades | Evaluación)
-- ============================================================

-- Limpieza de registros de prueba
DELETE FROM temas WHERE titulo = 'tamizaje prueba';

-- Si quieres dejar SOLO los temas de CONAFE, quita el guion doble
-- de la siguiente línea para borrar todo lo anterior:
-- DELETE FROM temas;


-- ============================================================
-- 1. CAMPO FORMATIVO: LENGUAJE Y COMUNICACIÓN
-- ============================================================

INSERT INTO temas (titulo, materia, grado, estado, condicion, objetivo, paso_a_paso) VALUES
('Cuentos y leyendas tradicionales de la comunidad',
 'Lenguaje y comunicación',
 'Preescolar y primaria',
 'Publicada',
 'Autismo (TEA)',
 'Que el aprendiente identifique personajes y secuencia narrativa de un cuento de su comunidad, apoyándose en imágenes fijas y material manipulable.',
 'Elección del tema: el tutor presenta tarjetas ilustradas de 3 cuentos locales. El niño elige la tarjeta del cuento que más le llama la atención.|Explicación del tema: el tutor lee el cuento párrafo por párrafo. Después de cada párrafo muestra imágenes fijas y señala a los personajes y sus acciones principales.|Actividades de comprensión: el niño recibe 3 tarjetas con las escenas del cuento y las coloca físicamente en un tablero velcro numerado (1 Inicio, 2 Desarrollo, 3 Final).|Evaluación: el niño señala o coloca el pictograma correcto cuando el tutor le pregunta quién es el personaje principal y qué pasó al final.');

INSERT INTO temas (titulo, materia, grado, estado, condicion, objetivo, paso_a_paso) VALUES
('Textos informativos sobre animales de la comunidad',
 'Lenguaje y comunicación',
 'Preescolar y primaria',
 'Publicada',
 'Autismo (TEA)',
 'Que el aprendiente reconozca las características reales de un animal de su entorno (alimentación, hábitat y desplazamiento) mediante clasificación visual.',
 'Elección del tema: el niño selecciona la foto de un animal comunitario (por ejemplo el perro, el caballo o la gallina) entre varias opciones visuales.|Explicación del tema: el tutor explica la ficha informativa de la UAI leyendo frases cortas y apoyándose en tarjetas con pictogramas de su alimentación, hábitat y desplazamiento.|Actividades de comprensión: el niño completa un cuadro clasificatorio pegando las tarjetas correspondientes en las columnas ¿Qué come? y ¿Dónde vive?|Evaluación: el tutor entrega 2 imágenes erróneas y 1 correcta. El niño debe seleccionar únicamente las características reales del animal estudiado.');

INSERT INTO temas (titulo, materia, grado, estado, condicion, objetivo, paso_a_paso) VALUES
('Carteles e instructivos de la vida cotidiana',
 'Lenguaje y comunicación',
 'Preescolar y primaria',
 'Publicada',
 'Autismo (TEA)',
 'Que el aprendiente siga y reconstruya la secuencia de un instructivo de la vida diaria a partir de apoyos visuales numerados.',
 'Elección del tema: el niño elige qué instructivo quiere realizar (por ejemplo armar una figura de papel o lavarse las manos).|Explicación del tema: el tutor explica paso a paso el instructivo mostrando cada acción con fotos numeradas del proceso.|Actividades de comprensión: el niño ejecuta físicamente cada paso del instructivo en orden directo, a medida que el tutor se lo muestra visualmente.|Evaluación: el tutor desordena las fotos del instructivo y el niño debe volver a organizarlas en la secuencia correcta sin ayuda.');


-- ============================================================
-- 2. CAMPO FORMATIVO: PENSAMIENTO MATEMÁTICO
-- ============================================================

INSERT INTO temas (titulo, materia, grado, estado, condicion, objetivo, paso_a_paso) VALUES
('Conteo y colecciones del entorno',
 'Pensamiento matemático',
 'Preescolar y primaria',
 'Publicada',
 'Autismo (TEA)',
 'Que el aprendiente establezca la correspondencia uno a uno entre una cantidad de objetos concretos y su representación numérica.',
 'Elección del tema: el estudiante elige el material concreto con el que desea contar (semillas, piedras o tapitas de colores).|Explicación del tema: el tutor muestra tarjetas con números e indica que cada número representa una cantidad exacta, demostrándolo al colocar semillas sobre puntos rojos dibujados.|Actividades de comprensión: el niño coloca físicamente las semillas en una caja de conteo con compartimentos numerados del 1 al 5.|Evaluación: el tutor coloca un grupo de 4 semillas en la mesa. El niño debe contar las semillas y entregar la tarjeta con el número 4 correcto.');

INSERT INTO temas (titulo, materia, grado, estado, condicion, objetivo, paso_a_paso) VALUES
('Operaciones básicas: suma y resta',
 'Pensamiento matemático',
 'Preescolar y primaria',
 'Publicada',
 'Autismo (TEA)',
 'Que el aprendiente comprenda la suma como juntar y la resta como quitar, resolviendo problemas prácticos con material manipulable.',
 'Elección del tema: el niño elige trabajar con el juego de la tiendita o con bloques de plástico encajables.|Explicación del tema: el tutor explica la suma como juntar y la resta como quitar, realizando demostraciones visibles con los bloques o monedas didácticas.|Actividades de comprensión: el tutor plantea ejercicios simples (tienes 2 bloques y te doy 2 más, ¿cuántos tienes?) y el niño manipula y junta los bloques físicamente.|Evaluación: el niño resuelve 3 tarjetas de problemas prácticos juntando o quitando sus bloques y seleccionando el resultado numérico.');

INSERT INTO temas (titulo, materia, grado, estado, condicion, objetivo, paso_a_paso) VALUES
('Fracciones y repartos equitativos',
 'Pensamiento matemático',
 'Preescolar y primaria',
 'Publicada',
 'Autismo (TEA)',
 'Que el aprendiente identifique la mitad como el reparto en dos partes iguales, comprobándolo con material físico fraccionable.',
 'Elección del tema: el niño elige qué objeto fraccionar (barras de plastilina o barras de bloques de colores).|Explicación del tema: el tutor muestra una barra entera de 4 partes y explica que al separarla en 2 partes iguales, cada parte es la mitad.|Actividades de comprensión: el niño separa la barra física de 4 bloques en 2 bloques azules y 2 bloques amarillos para formar mitades exactas.|Evaluación: el tutor muestra dos objetos, uno dividido a la mitad y otro en partes desiguales. El niño debe señalar cuál representa correctamente la mitad.');

INSERT INTO temas (titulo, materia, grado, estado, condicion, objetivo, paso_a_paso) VALUES
('Formas geométricas y cuerpos en la naturaleza',
 'Pensamiento matemático',
 'Preescolar y primaria',
 'Publicada',
 'Autismo (TEA)',
 'Que el aprendiente clasifique objetos de su comunidad según su forma geométrica, reforzando el reconocimiento táctil y visual de los bordes.',
 'Elección del tema: el niño elige qué colección de formas explorar (figuras geométricas planas o cuerpos tridimensionales de la comunidad).|Explicación del tema: el tutor presenta objetos reales (cajas, pelotas, conos) y muestra la tarjeta con el símbolo de la forma, resaltando sus bordes de forma táctil.|Actividades de comprensión: el niño clasifica diversos objetos de la comunidad colocándolos en 3 recipientes rotulados con la forma geométrica que les corresponde.|Evaluación: el tutor muestra un objeto nuevo del aula (por ejemplo un libro) y el niño debe emparejarlo con la tarjeta de la figura geométrica correcta.');

INSERT INTO temas (titulo, materia, grado, estado, condicion, objetivo, paso_a_paso) VALUES
('Medición, pesos y longitudes',
 'Pensamiento matemático',
 'Preescolar y primaria',
 'Publicada',
 'Autismo (TEA)',
 'Que el aprendiente compare objetos por peso y longitud usando instrumentos de medición concretos y vocabulario comparativo.',
 'Elección del tema: el niño selecciona la herramienta de medición que quiere usar (balanza de platillos o cinta de medir visual).|Explicación del tema: el tutor explica la diferencia entre más pesado y más ligero usando la balanza, o más largo y más corto usando tiras de papel de colores.|Actividades de comprensión: el niño coloca dos objetos en los platillos de la balanza o compara dos tiras de madera alineándolas en la mesa.|Evaluación: el tutor le pide entregar el objeto más pesado o la tira más larga entre dos opciones dadas, y el niño realiza la selección correcta.');


-- ============================================================
-- 3. CAMPO FORMATIVO: EXPLORACIÓN DEL MUNDO NATURAL Y SOCIAL
-- ============================================================

INSERT INTO temas (titulo, materia, grado, estado, condicion, objetivo, paso_a_paso) VALUES
('El cuerpo humano y los órganos vitales',
 'Exploración del mundo natural y social',
 'Preescolar y primaria',
 'Publicada',
 'Autismo (TEA)',
 'Que el aprendiente ubique los órganos principales en el cuerpo humano y asocie cada uno con su función mediante apoyos visuales.',
 'Elección del tema: el estudiante elige explorar el tema del cuerpo humano en el catálogo visual.|Explicación del tema: el tutor explica la función de los órganos principales (corazón, estómago, pulmones) usando un póster con modelos tridimensionales con velcro.|Actividades de comprensión: el niño toma las piezas de los órganos de la mesa y las adhiere sobre la silueta del cuerpo humano en la posición correcta.|Evaluación: el tutor señala un órgano en la silueta y el niño debe asociarlo con su función mediante tarjetas visuales.');

INSERT INTO temas (titulo, materia, grado, estado, condicion, objetivo, paso_a_paso) VALUES
('Las plantas y el cuidado del medio ambiente',
 'Exploración del mundo natural y social',
 'Preescolar y primaria',
 'Publicada',
 'Autismo (TEA)',
 'Que el aprendiente identifique y ensamble las partes de una planta, reconociendo su orden natural de crecimiento.',
 'Elección del tema: el niño elige entre investigar las partes de una planta real o la clasificación del reciclaje.|Explicación del tema: el tutor muestra plantas reales traídas de la comunidad y explica sus partes (raíz, tallo, hoja, flor) permitiéndole tocarlas.|Actividades de comprensión: el estudiante separa y clasifica las partes de las plantas en 4 recipientes etiquetados visualmente.|Evaluación: el tutor entrega una planta desarmada en piezas de cartón. El niño la ensambla correctamente de abajo hacia arriba: raíz, tallo, hoja y flor.');


-- ============================================================
-- 4. CAMPO FORMATIVO: HISTORIA, GEOGRAFÍA Y CONVIVENCIA
-- ============================================================

INSERT INTO temas (titulo, materia, grado, estado, condicion, objetivo, paso_a_paso) VALUES
('Mi comunidad, croquis y trayectos',
 'Historia, geografía y convivencia',
 'Preescolar y primaria',
 'Publicada',
 'Autismo (TEA)',
 'Que el aprendiente se oriente en una representación de su comunidad identificando puntos clave y trazando trayectos cotidianos.',
 'Elección del tema: el niño selecciona la maqueta de la comunidad para estudiar su entorno local.|Explicación del tema: el tutor explica cómo guiarse en la comunidad identificando puntos clave (casa, escuela, tienda, iglesia) en una maqueta con texturas.|Actividades de comprensión: el niño mueve un carrito o figura por la maqueta siguiendo el camino desde su casa hasta la escuela.|Evaluación: el tutor le pide llevar la figura a un lugar específico, por ejemplo la tienda. El niño debe realizar el recorrido correcto de forma autónoma.');


-- Verificación
SELECT id, materia, titulo, estado FROM temas ORDER BY id;