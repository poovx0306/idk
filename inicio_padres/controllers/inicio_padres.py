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

        cur.execute("SELECT correo, nombre FROM usuario WHERE rol = 'padre' AND id_referencia = ?", (id_padre,))
        usuario = cur.fetchone()
        nombre_completo = usuario["nombre"] if usuario else (session.nombre or "Familia")
        correo = usuario["correo"] if usuario else ""

        partes_nombre = nombre_completo.split()
        apellidos_familia = " ".join(partes_nombre[1:]) if len(partes_nombre) > 1 else nombre_completo

        cur.execute("SELECT id_infante, nombre FROM infantes WHERE id_padres = ?", (id_padre,))
        ninos = cur.fetchall()
        total_ninos = len(ninos)

        cur.execute("""
            SELECT COUNT(*) AS total FROM resultados r
            JOIN infantes i ON i.id_infante = r.id_infante1
            WHERE i.id_padres = ?
        """, (id_padre,))
        total_cuestionarios = cur.fetchone()["total"]

        cur.execute("SELECT COUNT(*) AS total FROM actividad_casa")
        total_actividades_casa = cur.fetchone()["total"] or 0

        cur.execute("""
            SELECT COUNT(*) AS hechas
            FROM actividad_casa_realizada acr
            JOIN infantes i ON i.id_infante = acr.id_infante
            WHERE i.id_padres = ?
        """, (id_padre,))
        hechas_casa = cur.fetchone()["hechas"] or 0

        total_posible = total_actividades_casa * total_ninos
        progreso_pct = round((hechas_casa / total_posible) * 100) if total_posible > 0 else 0

        cur.execute("""
            SELECT r.id_resultado, r.fecha, r.nivel_riesgo, i.nombre AS nombre_infante
            FROM resultados r
            JOIN infantes i ON i.id_infante = r.id_infante1
            WHERE i.id_padres = ?
            ORDER BY r.fecha DESC
            LIMIT 2
        """, (id_padre,))
        historial = cur.fetchall()

        alerta = bool(historial)

        cur.execute(CONSEJOS_ROTATIVOS_QUERY)
        consejos = cur.fetchall()
        consejo_hoy = None
        if consejos:
            dia_del_anio = time.localtime().tm_yday
            consejo_hoy = consejos[dia_del_anio % len(consejos)]

        conn.close()

        return render.inicio_padres(
            "inicio", apellidos_familia, nombre_completo, correo, total_cuestionarios, total_ninos,
            progreso_pct, historial, alerta, consejo_hoy
        )