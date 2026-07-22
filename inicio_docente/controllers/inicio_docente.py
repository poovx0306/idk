import web
import sqlite3

render = web.template.render('inicio_docente/views')


class InicioDocente:
    def GET(self):
        datos = web.input(id="1")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        cursor.execute("SELECT nombre FROM docente WHERE id_docente = ?", (id_docente,))
        docente = cursor.fetchone()
        nombre_docente = docente["nombre"] if docente else "Docente"

        cursor.execute("SELECT COUNT(*) FROM estrategias_didacticas")
        total_estrategias = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM infante WHERE id_docente = ?", (id_docente,))
        total_alumnos = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM actividad_asignada WHERE id_docente = ? AND DATE(fecha_asignacion) = DATE('now')",
            (id_docente,),
        )
        total_actividades = cursor.fetchone()[0]

        conexion.close()

        return render.inicio_docente(nombre_docente, total_estrategias, total_alumnos, total_actividades)