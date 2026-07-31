CREATE TABLE IF NOT EXISTS actividad_favorita (
    id_docente INTEGER REFERENCES docente(id_docente),
    id_actividad INTEGER REFERENCES actividad_asignada(id),
    PRIMARY KEY (id_docente, id_actividad)
);