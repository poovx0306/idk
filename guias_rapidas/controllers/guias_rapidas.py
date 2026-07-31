import web
import sqlite3

render = web.template.render('guias_rapidas/views')


class GuiasRapidas:
    """Muestra las guías rápidas organizadas por categoría."""

    def GET(self):
        datos = web.input(id="1")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        cursor.execute("SELECT categoria, titulo, contenido FROM guia_rapida ORDER BY categoria, id")
        filas = cursor.fetchall()
        conexion.close()

        categorias = {}
        for fila in filas:
            cat = fila["categoria"]
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append({"titulo": fila["titulo"], "contenido": fila["contenido"]})

        return render.guias_rapidas(id_docente, categorias)