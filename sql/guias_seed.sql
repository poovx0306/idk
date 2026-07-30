CREATE TABLE IF NOT EXISTS guia_rapida (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT NOT NULL,
    titulo TEXT NOT NULL,
    contenido TEXT NOT NULL
);

DELETE FROM guia_rapida;

INSERT INTO guia_rapida (categoria, titulo, contenido) VALUES
('Comunicación', 'Usa frases cortas y directas', 'Evita el lenguaje figurado (sarcasmo, dobles sentidos). Da instrucciones simples y de un solo paso a la vez.'),
('Comunicación', 'Apóyate en lo visual', 'Pictogramas, dibujos o listas escritas ayudan a que la instrucción se entienda mejor que solo con palabras.'),
('Comunicación', 'Da tiempo para responder', 'Después de una pregunta o instrucción, espera unos segundos antes de repetirla. Procesar la información puede tomar más tiempo.'),
('Rutinas y estructura', 'Anticipa los cambios', 'Avisa con anticipación cuando algo va a cambiar en la actividad o el horario. Una agenda visual del día reduce la ansiedad.'),
('Rutinas y estructura', 'Mantén una rutina constante', 'El orden y la repetición dan seguridad. Entrar, iniciar y cerrar la clase siempre de forma parecida ayuda a ubicarse.'),
('Rutinas y estructura', 'Divide las tareas en pasos', 'Una actividad grande puede abrumar. Preséntala como una serie de pasos pequeños y claros.'),
('Regulación sensorial', 'Reduce estímulos innecesarios', 'Menos ruido, luces menos intensas y espacios menos saturados ayudan a mantener la concentración.'),
('Regulación sensorial', 'Ten un espacio de calma disponible', 'Un rincón tranquilo al que el alumno pueda ir cuando se sienta abrumado previene crisis mayores.'),
('Regulación sensorial', 'Permite movimiento o materiales sensoriales', 'Objetos para manipular con las manos o pausas activas pueden ayudar a mantener la atención.'),
('Interacción social', 'Enseña de forma explícita las normas sociales', 'Cosas que otros niños aprenden solas (turnos, saludos) puede que necesiten explicarse paso a paso.'),
('Interacción social', 'Facilita el juego con otros compañeros', 'Actividades estructuradas con roles claros ayudan a que la interacción con el grupo sea menos abrumadora.'),
('Refuerzo positivo', 'Reconoce los logros pequeños', 'Un elogio específico e inmediato como Muy bien, guardaste tus cosas solo refuerza mejor que uno general.'),
('Refuerzo positivo', 'Sé constante entre la escuela y la casa', 'Cuando docentes y familia usan las mismas señales o recompensas, el aprendizaje se refuerza más rápido.');