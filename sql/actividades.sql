ALTER TABLE actividad_asignada ADD COLUMN titulo TEXT;
ALTER TABLE actividad_asignada ADD COLUMN objetivo TEXT;
ALTER TABLE actividad_asignada ADD COLUMN materiales TEXT;
ALTER TABLE actividad_asignada ADD COLUMN paso_a_paso TEXT;
ALTER TABLE actividad_asignada ADD COLUMN materia TEXT;
ALTER TABLE actividad_asignada ADD COLUMN grado TEXT;
ALTER TABLE actividad_asignada ADD COLUMN grupo TEXT;
ALTER TABLE actividad_asignada ADD COLUMN estado TEXT DEFAULT 'Pendiente';
ALTER TABLE actividad_asignada ADD COLUMN fecha_limite TEXT;

UPDATE actividad_asignada SET
  titulo = 'Conteo con material concreto para el aula',
  objetivo = 'Reforzar la nocion de numero usando objetos manipulables antes de pasar al papel.',
  materiales = 'Fichas o piedras pequenas · Charola o superficie plana · Tarjetas con numeros del 1 al 10',
  paso_a_paso = 'Reune los objetos y colocalos frente al alumno.|Muestra una tarjeta con un numero y dila en voz alta.|Pide al alumno que cuente esa cantidad de objetos y los separe.|Revisen juntos contando de nuevo en voz alta.|Registra si la cantidad fue correcta.',
  materia = 'Matematicas', grado = '2°', grupo = '2 A', estado = 'Pendiente', fecha_limite = '2026-08-05'
WHERE id = 1;

UPDATE actividad_asignada SET
  titulo = 'Rutina visual de inicio de clase',
  objetivo = 'Anticipar el orden de actividades del dia para reducir la ansiedad al iniciar la clase.',
  materiales = 'Tarjetas con pictogramas de cada actividad · Franja o riel para colocarlas · Velcro o cinta adhesiva',
  paso_a_paso = 'Antes de que lleguen los alumnos, coloca las tarjetas en el orden del dia.|Al iniciar, revisa la franja completa con el grupo en voz alta.|Antes de cada cambio, senala la siguiente tarjeta.|Retira la tarjeta de la actividad terminada junto con el alumno.|Cierra el dia repasando las tarjetas completadas.',
  materia = 'Habilidades sociales', grado = '1°', grupo = '1 A', estado = 'Completada', fecha_limite = '2026-07-28'
WHERE id = 2;

INSERT INTO actividad_asignada (id_docente, id_infante, descripcion, fecha_asignacion, titulo, objetivo, materiales, paso_a_paso, materia, grado, grupo, estado, fecha_limite) VALUES
(1, 1, 'Reconocimiento de emociones con pictogramas', DATE('now'),
 'Reconocimiento de emociones con pictogramas',
 'Que el alumno asocie una emocion basica con su pictograma correspondiente.',
 'Tarjetas con pictogramas de emociones (feliz, triste, enojado, sorprendido) · Espejo pequeno',
 'Muestra una tarjeta de emocion y nombrala en voz alta.|Pide al alumno que imite la expresion frente al espejo.|Pregunta cuando se ha sentido asi el mismo.|Repite con las 4 emociones y revisen juntos cuales le costaron mas.',
 'Español', '2°', '2 A', 'Pendiente', '2026-08-10'),

(1, 2, 'Sumas con material concreto y dibujo', DATE('now'),
 'Sumas con material concreto y dibujo',
 'Pasar de la suma con objetos reales al dibujo antes de la operacion escrita.',
 'Dos grupos de fichas de colores distintos · Hojas blancas · Crayones',
 'Forma dos grupos de fichas de colores distintos.|Cuenta cada grupo por separado en voz alta.|Junta ambos grupos y cuenta el total.|Dibuja los grupos en la hoja en vez de los objetos.|Escribe la operacion con numeros junto al dibujo.',
 'Matematicas', '2°', '2 B', 'Pendiente', '2026-08-07'),

(1, 1, 'Ensartado de cuentas para motricidad fina', DATE('now'),
 'Ensartado de cuentas para motricidad fina',
 'Fortalecer la pinza digital y la concentracion mediante ensartado.',
 'Cuentas grandes de colores · Agujetas o cordones gruesos · Charola pequena',
 'Coloca las cuentas y el cordon en la charola frente al alumno.|Muestra como ensartar una cuenta despacio.|Pide al alumno que ensarte 5 cuentas a su ritmo.|Anima cada logro con una frase especifica y breve.',
 'Motricidad', '1°', '1 A', 'Pendiente', '2026-08-03'),

(1, 2, 'Lectura global de palabras con imagen', DATE('now'),
 'Lectura global de palabras con imagen',
 'Asociar una palabra escrita con su imagen y objeto correspondiente.',
 'Tarjetas con imagen y palabra (casa, coche, arbol, perro) · Objetos o dibujos reales de cada palabra',
 'Muestra la tarjeta y lee la palabra en voz alta senalandola.|Pide al alumno que busque el objeto o dibujo que corresponde.|Repite mezclando el orden de las tarjetas.|Quita la imagen y deja solo la palabra para ver si la reconoce.',
 'Español', '3°', '3 A', 'Completada', '2026-07-25'),

(1, 1, 'Plastilina para fortalecer los musculos de la mano', DATE('now'),
 'Plastilina para fortalecer los musculos de la mano',
 'Fortalecer la musculatura de la mano como base para la escritura.',
 'Plastilina o masa moldeable · Tapete o charola para trabajar · Moldes simples (opcional)',
 'Da al alumno una porcion de plastilina para amasar libremente.|Pide que haga bolitas pequenas apretando con los dedos.|Pide que aplane la plastilina con la palma de la mano.|Cierra la actividad guardando el material juntos.',
 'Motricidad', '2°', '2 A', 'Pendiente', '2026-08-12'),

(1, 2, 'Historia social para pedir un descanso', DATE('now'),
 'Historia social para pedir un descanso',
 'Ensenar una forma clara de pedir una pausa cuando se siente abrumado.',
 'Tarjeta con la frase "Necesito un descanso" · Espacio tranquilo designado en el aula',
 'Explica la situacion: a veces nos sentimos abrumados y podemos pedir un descanso.|Practica la frase exacta usando la tarjeta.|Muestra donde esta el espacio tranquilo asignado.|Practica el uso de la tarjeta en un momento sin presion antes de necesitarla de verdad.',
 'Habilidades sociales', '3°', '3 A', 'Pendiente', '2026-08-09');