import web
import sqlite3
import os
import datetime
import google.generativeai as genai

render = web.template.render('avance_infante/views')

db_path = "sql/conaap.db"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


def generar_analisis_ia(id_infante, evolucion, hechas_act, total_act, racha):
    hoy = str(datetime.date.today())

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "SELECT texto FROM analisis_evolucion_ia WHERE id_infante = ? AND fecha = ?",
        (id_infante, hoy)
    )
    fila = cur.fetchone()
    if fila:
        conn.close()
        return fila["texto"]

    if not GEMINI_API_KEY:
        conn.close()
        return "El análisis con IA no está disponible en este momento (falta configurar la API key)."

    resumen_resultados = "\n".join(
        f"- {r['fecha']}: nivel de riesgo {r['nivel_riesgo']}" for r in evolucion
    ) or "No hay cuestionarios respondidos todavía."

    prompt = f"""Eres un asistente que ayuda a padres de niños con autismo (TEA) a entender el progreso de su hijo,
de forma cálida, breve y sin tecnicismos.

Datos disponibles:
- Historial de niveles de riesgo por cuestionario (en orden cronológico):
{resumen_resultados}
- Actividades asignadas por el docente: {hechas_act} completadas de {total_act}.
- Días distintos en los que se completó una actividad post-crisis: {racha}.

Escribe un análisis breve (máximo 4-5 líneas) en español, dirigido directamente al padre/madre,
que correlacione la constancia en las actividades post-crisis y las actividades asignadas con la
evolución del nivel de riesgo. Sé honesto pero alentador, sin dar diagnósticos médicos."""

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        modelo = genai.GenerativeModel("gemini-flash-latest")
        respuesta = modelo.generate_content(prompt)
        texto = respuesta.text.strip()
    except Exception:
        conn.close()
        return "No se pudo generar el análisis en este momento. Intenta más tarde."

    cur.execute(
        "INSERT INTO analisis_evolucion_ia (id_infante, texto, fecha) VALUES (?, ?, ?)",
        (id_infante, texto, hoy)
    )
    conn.commit()
    conn.close()

    return texto


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

        cur.execute(
            "SELECT COUNT(DISTINCT fecha) AS racha FROM actividad_postcrisis_realizada WHERE id_infante = ?",
            (id_infante,)
        )
        racha = cur.fetchone()["racha"] or 0

        conn.close()

        analisis = generar_analisis_ia(id_infante, evolucion, hechas_act, total_act, racha)

        return render.avance_infante(
            "avance", evolucion, progreso_pct, hechas_act, total_act, racha, analisis
        )