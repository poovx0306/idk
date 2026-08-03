import web
import sqlite3
import time

render = web.template.render('inicio_padres/views')

db_path = "sql/conaap.db"

CONSEJOS_ROTATIVOS_QUERY = "SELECT titulo, contenido FROM guia_rapida WHERE publico IN ('padre','ambos') ORDER BY id"

class InicioPadres:
    def GET(self):
        session = web.config._session
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        id_padre = session.id_referencia

        cur.execute("SELECT id_infante, nombre FROM infantes WHERE id_padres = ?", (id_padre,))
        ninos = cur.fetchall()
        total_ninos = len(ninos)

        cur.execute("""
            SELECT COUNT(*) AS total FROM resultados r
            JOIN infantes i ON i.id_infante = r.id_infante1
            WHERE i.id_padres = ?
        """, (id_padre,))
        total_cuestionarios = cur.fetchone()["total"]

        cur.execute("SELECT COUNT(*) FROM actividad_postcrisis")
        total_postcrisis = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT COUNT(DISTINCT r.id_actividad) FROM actividad_postcrisis_realizada r
            JOIN infantes i ON i.id_infante = r.id_infante
            WHERE i.id_padres = ?
        """, (id_padre,))
        postcrisis_realizadas = cur.fetchone()[0] or 0

        progreso_pct = round((postcrisis_realizadas / total_postcrisis) * 100) if total_postcrisis > 0 else 0

        cur.execute("""
            SELECT r.id_resultado, r.fecha, r.nivel_riesgo, i.nombre AS nombre_infante
            FROM resultados r
            JOIN infantes i ON i.id_infante = r.id_infante1
            WHERE i.id_padres = ?
            ORDER BY r.fecha DESC
            LIMIT 2
        """, (id_padre,))
        historial = cur.fetchall()

        alerta = historial and historial[0]["nivel_riesgo"] in ("Medio", "Alto")

        cur.execute(CONSEJOS_ROTATIVOS_QUERY)
        consejos = cur.fetchall()
        consejo_hoy = None
        if consejos:
            dia_del_anio = time.localtime().tm_yday
            consejo_hoy = consejos[dia_del_anio % len(consejos)]

        conn.close()

        return render.inicio_padres(
            "inicio", session.nombre, total_cuestionarios, total_ninos,
            progreso_pct, historial, alerta, consejo_hoy
        )