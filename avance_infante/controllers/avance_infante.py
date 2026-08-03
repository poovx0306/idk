import web
import sqlite3
from datetime import date

render = web.template.render('avance_infante/views')

db_path = "sql/conaap.db"

def actualizar_racha(id_infante):
    semana_actual = date.today().isocalendar()[1]
    anio_actual = date.today().isocalendar()[0]
    clave_semana = f"{anio_actual}-{semana_actual}"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM racha_infante WHERE id_infante = ?", (id_infante,))
    fila = cur.fetchone()

    if fila is None:
        cur.execute(
            "INSERT INTO racha_infante (id_infante, racha_actual, racha_maxima, ultima_semana_iso) VALUES (?, 1, 1, ?)",
            (id_infante, clave_semana)
        )
    elif fila["ultima_semana_iso"] == clave_semana:
        pass
    else:
        nueva_racha = fila["racha_actual"] + 1
        nueva_maxima = max(nueva_racha, fila["racha_maxima"])
        cur.execute(
            "UPDATE racha_infante SET racha_actual = ?, racha_maxima = ?, ultima_semana_iso = ? WHERE id_infante = ?",
            (nueva_racha, nueva_maxima, clave_semana, id_infante)
        )
    conn.commit()
    conn.close()

class AvanceInfante:
    def GET(self):
        session = web.config._session
        id_infante = session.id_infante_actual

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT fecha, nivel_riesgo FROM resultados WHERE id_infante1 = ? ORDER BY fecha", (id_infante,))
        evolucion = cur.fetchall()

        cur.execute("""
            SELECT COUNT(*) AS total, SUM(CASE WHEN estado='Completada' THEN 1 ELSE 0 END) AS hechas
            FROM actividad_asignada WHERE id_infante = ?
        """, (id_infante,))
        act = cur.fetchone()
        total_act = act["total"] or 0
        hechas_act = act["hechas"] or 0
        progreso_pct = round((hechas_act / total_act) * 100) if total_act > 0 else 0

        cur.execute("SELECT racha_actual, racha_maxima FROM racha_infante WHERE id_infante = ?", (id_infante,))
        racha = cur.fetchone()

        conn.close()

        return render.avance_infante(
            "avance", evolucion, progreso_pct, hechas_act, total_act, racha
        )