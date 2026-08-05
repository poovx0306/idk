import web
import sqlite3

render = web.template.render('mi_perfil_docente/views')


class MiPerfil:
    def GET(self):
        datos = web.input(id="1")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id_docente, nombre, clave_docente, correo FROM docente WHERE id_docente = ?",
            (id_docente,),
        )
        docente = cursor.fetchone()

        if not docente:
            conexion.close()
            return "Docente no encontrado"

        cursor.execute("SELECT COUNT(*) FROM infantes WHERE id_docente1 = ?", (id_docente,))
        total_alumnos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM actividad_asignada WHERE id_docente = ?", (id_docente,))
        total_asignadas = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM actividad_asignada WHERE id_docente = ? AND estado = 'Completada'",
            (id_docente,),
        )
        total_completadas = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM actividad_favorita WHERE id_docente = ?", (id_docente,))
        total_guardadas = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM crisis_atendida WHERE id_docente = ?", (id_docente,))
        total_crisis = cursor.fetchone()[0]

        conexion.close()

        return render.mi_perfil(
            docente["id_docente"],
            docente["nombre"],
            docente["clave_docente"],
            docente["correo"],
            total_alumnos,
            total_asignadas,
            total_completadas,
            total_guardadas,
            total_crisis,
        )