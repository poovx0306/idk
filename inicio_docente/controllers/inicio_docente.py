import web
import sqlite3
import datetime

render = web.template.render('inicio_docente/views')


class InicioDocente:
    def GET(self):
        datos = web.input(id="1")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        cursor.execute("""
        SELECT docente.nombre, usuario.correo
        FROM docente
        JOIN usuario ON usuario.id_referencia = docente.id_docente AND usuario.rol = 'docente'
        WHERE docente.id_docente = ?
        """, (id_docente,))

        docente = cursor.fetchone()
        nombre_docente = docente["nombre"] if docente else "Docente"
        correo_docente = docente["correo"] if docente else "sin-correo@conafe.gob.mx"

        cursor.execute("SELECT COUNT(*) FROM temas WHERE estado = 'Publicada'")
        total_estrategias = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM infantes WHERE id_docente1 = ?", (id_docente,))
        total_alumnos = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM retroalimentacion WHERE id_docente = ? AND fecha = DATE('now')",
            (id_docente,),
        )
        total_evaluaciones_hoy = cursor.fetchone()[0]

        cursor.execute("SELECT contenido FROM guia_rapida ORDER BY id")
        consejos = cursor.fetchall()
        if consejos:
            indice = datetime.date.today().timetuple().tm_yday % len(consejos)
            consejo_dia = consejos[indice]["contenido"]
        else:
            consejo_dia = "Anticipa los cambios de actividad con una agenda visual. Para un alumno con autismo, saber qué sigue reduce la ansiedad y previene crisis en el aula."

        conexion.close()

        return render.inicio_docente(
            id_docente, nombre_docente, correo_docente,
            total_estrategias, total_alumnos, total_evaluaciones_hoy, consejo_dia
        )