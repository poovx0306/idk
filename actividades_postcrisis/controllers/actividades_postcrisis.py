import web
import sqlite3
from datetime import date

render = web.template.render('actividades_postcrisis/views')

db_path = "sql/conaap.db"


class ActividadesPostcrisis:
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
            return render.actividades_postcrisis_seleccion("postcrisis", ninos)

        id_infante = int(datos.id_infante)

        cur.execute("SELECT nombre FROM infantes WHERE id_infante = ?", (id_infante,))
        infante = cur.fetchone()
        nombre_infante = infante["nombre"] if infante else ""

        cur.execute("SELECT id_actividad, titulo, descripcion, duracion_min, pasos FROM actividad_postcrisis")
        actividades = cur.fetchall()

        cur.execute(
            "SELECT id_actividad FROM actividad_postcrisis_realizada WHERE id_infante = ? AND fecha = ?",
            (id_infante, str(date.today()))
        )
        hechas_hoy_ids = set(row["id_actividad"] for row in cur.fetchall())

        conn.close()

        return render.actividades_postcrisis("postcrisis", id_infante, nombre_infante, actividades, hechas_hoy_ids)


class MarcarActividadPostcrisis:
    def POST(self):
        datos = web.input(id_actividad=None, id_infante=None)
        id_infante = int(datos.id_infante)
        id_actividad = int(datos.id_actividad)

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO actividad_postcrisis_realizada (id_infante, id_actividad, fecha) VALUES (?, ?, ?)",
            (id_infante, id_actividad, str(date.today()))
        )
        conn.commit()
        conn.close()

        raise web.HTTPError('303 See Other', {'Location': '/padre/postcrisis?id_infante=%s' % id_infante})