import web
import sqlite3
import datetime

render = web.template.render('actividades_casa/views')

db_path = "sql/conaap.db"


class ActividadesCasa:
    def GET(self):
        session = web.config._session
        datos = web.input(id_infante=None)

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        if not datos.id_infante:
            id_padres = session.id_referencia
            cur.execute("SELECT id_infante, nombre, edad FROM infantes WHERE id_padres = ?", (id_padres,))
            ninos = cur.fetchall()
            conn.close()
            return render.actividades_casa_seleccion("casa", ninos)

        id_infante = int(datos.id_infante)

        cur.execute("SELECT nombre FROM infantes WHERE id_infante = ?", (id_infante,))
        infante = cur.fetchone()
        nombre_infante = infante["nombre"] if infante else ""

        cur.execute("SELECT id, titulo, descripcion, edad_recomendada FROM actividad_casa ORDER BY id")
        actividades = cur.fetchall()

        cur.execute("SELECT id_actividad FROM actividad_casa_realizada WHERE id_infante = ?", (id_infante,))
        hechas_ids = set(row["id_actividad"] for row in cur.fetchall())

        conn.close()

        return render.actividades_casa("casa", id_infante, nombre_infante, actividades, hechas_ids)


class MarcarActividadCasa:
    def POST(self):
        datos = web.input(id_infante=None, id_actividad=None)
        id_infante = int(datos.id_infante)
        id_actividad = int(datos.id_actividad)

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO actividad_casa_realizada (id_infante, id_actividad, fecha) VALUES (?, ?, ?)",
            (id_infante, id_actividad, str(datetime.date.today()))
        )
        conn.commit()
        conn.close()

        raise web.HTTPError('303 See Other', {'Location': '/padre/actividades-casa?id_infante=%s' % id_infante})