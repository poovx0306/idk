import web
import sqlite3
from datetime import date

render = web.template.render('actividades_postcrisis/views')

db_path = "sql/conaap.db"

class ActividadesPostcrisis:
    def GET(self):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id_actividad, titulo, descripcion, duracion_min, pasos FROM actividad_postcrisis")
        actividades = cur.fetchall()
        conn.close()
        return render.actividades_postcrisis("postcrisis", actividades)

class MarcarActividadPostcrisis:
    def POST(self):
        session = web.config._session
        datos = web.input(id_actividad=None)
        id_infante = session.id_infante_actual

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO actividad_postcrisis_realizada (id_infante, id_actividad, fecha) VALUES (?, ?, ?)",
            (id_infante, datos.id_actividad, str(date.today()))
        )
        conn.commit()
        conn.close()

        from avance_infante.controllers.avance_infante import actualizar_racha
        actualizar_racha(id_infante)

        raise web.HTTPError('303 See Other', {'Location': '/padre/postcrisis'})