import web
import sqlite3

render = web.template.render('estrategias_didacticas/views')


class EstrategiasDidacticas:
    def GET(self):
        datos = web.input(id="1", condicion="Autismo (TEA)", materia="", grado="")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        cursor.execute("SELECT nombre FROM docente WHERE id_docente = ?", (id_docente,))
        docente = cursor.fetchone()
        nombre_docente = docente["nombre"] if docente else "Docente"

        consulta = "SELECT * FROM estrategias_didacticas WHERE 1=1"
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

        cursor.execute(consulta, parametros)
        estrategias = cursor.fetchall()

        conexion.close()

        return render.estrategias_didacticas(
            id_docente, nombre_docente, estrategias,
            datos.condicion, datos.materia, datos.grado
        )


class FichaActividad:
    def GET(self):
        datos = web.input(id_estrategia="", id="1")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        cursor.execute("SELECT nombre FROM docente WHERE id_docente = ?", (id_docente,))
        docente = cursor.fetchone()
        nombre_docente = docente["nombre"] if docente else "Docente"

        cursor.execute(
            "SELECT * FROM estrategias_didacticas WHERE id_estrategia = ?",
            (datos.id_estrategia,)
        )
        estrategia = cursor.fetchone()
        conexion.close()

        if not estrategia:
            raise web.notfound()

        texto_pasos = estrategia["paso_a_paso"] or ""
        pasos = [p.strip() for p in texto_pasos.split("|") if p.strip()]

        return render.ficha_actividad(id_docente, nombre_docente, estrategia, pasos)