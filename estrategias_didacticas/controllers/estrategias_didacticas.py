import web
import sqlite3

render = web.template.render('estrategias_didacticas/views')


def obtener_docente(cursor, id_docente):
    cursor.execute("""
        SELECT docente.nombre, usuario.correo
        FROM docente
        JOIN usuario ON usuario.id_referencia = docente.id_docente AND usuario.rol = 'docente'
        WHERE docente.id_docente = ?
    """, (id_docente,))
    fila = cursor.fetchone()
    nombre = fila["nombre"] if fila else "Docente"
    correo = fila["correo"] if fila else "sin-correo@conafe.gob.mx"
    return nombre, correo


class EstrategiasDidacticas:
    def GET(self):
        datos = web.input(id="1", condicion="Autismo (TEA)", materia="", grado="")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        nombre_docente, correo_docente = obtener_docente(cursor, id_docente)

        consulta = "SELECT * FROM temas WHERE estado = 'Publicada'"
        parametros = []

        if datos.condicion:
            consulta += " AND condicion = ?"
            parametros.append(datos.condicion)
        if datos.materia:
            consulta += " AND materia = ?"
            parametros.append(datos.materia)
        if datos.grado:
            consulta += " AND grado = ?"
            parametros.append(datos.grado)

        consulta += " ORDER BY materia, titulo"

        cursor.execute(consulta, parametros)
        estrategias = cursor.fetchall()

        cursor.execute(
            "SELECT DISTINCT materia FROM temas "
            "WHERE estado = 'Publicada' AND materia IS NOT NULL AND materia <> '' "
            "ORDER BY materia"
        )
        lista_materias = [fila["materia"] for fila in cursor.fetchall()]

        cursor.execute(
            "SELECT DISTINCT grado FROM temas "
            "WHERE estado = 'Publicada' AND grado IS NOT NULL AND grado <> '' "
            "ORDER BY grado"
        )
        lista_grados = [fila["grado"] for fila in cursor.fetchall()]

        conexion.close()

        return render.estrategias_didacticas(
            id_docente, nombre_docente, correo_docente, estrategias,
            datos.condicion, datos.materia, datos.grado,
            lista_materias, lista_grados
        )


class FichaActividad:
    def GET(self):
        datos = web.input(id_estrategia="", id="1")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        nombre_docente, correo_docente = obtener_docente(cursor, id_docente)

        cursor.execute(
            "SELECT * FROM temas WHERE id = ?",
            (datos.id_estrategia,)
        )
        estrategia = cursor.fetchone()
        conexion.close()

        if not estrategia:
            raise web.notfound()

        texto_pasos = estrategia["paso_a_paso"] or ""
        pasos = [p.strip() for p in texto_pasos.split("|") if p.strip()]

        return render.ficha_actividad(id_docente, nombre_docente, correo_docente, estrategia, pasos)