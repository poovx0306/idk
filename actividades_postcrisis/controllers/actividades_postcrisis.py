import web
import sqlite3
from datetime import date

render = web.template.render('actividades_postcrisis/views')

db_path = "sql/conaap.db"


def _listar(id_infante, id_recien_marcada=None):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT ap.id_actividad, ap.titulo, ap.descripcion, ap.duracion_min, ap.pasos,
        CASE WHEN EXISTS (
            SELECT 1 FROM actividad_postcrisis_realizada r
            WHERE r.id_actividad = ap.id_actividad
              AND r.id_infante = ?
              AND date(r.fecha) = date('now')
        ) THEN 1 ELSE 0 END AS completada_hoy
        FROM actividad_postcrisis ap
    """, (id_infante,))
    actividades = cur.fetchall()
    conn.close()
    return render.actividades_postcrisis("postcrisis", actividades, id_recien_marcada)


class ActividadesPostcrisis:
    def GET(self):
        session = web.config._session
        id_infante = session.id_infante_actual
        return _listar(id_infante)


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

        return _listar(id_infante, id_recien_marcada=datos.id_actividad)