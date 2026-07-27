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

        conexion.close()

        if not docente:
            return "Docente no encontrado"

        return render.mi_perfil(
            docente["id_docente"],
            docente["nombre"],
            docente["clave_docente"],
            docente["correo"],
            "Febrero 2025",  
        )