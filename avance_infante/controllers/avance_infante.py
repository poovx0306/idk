import web
import sqlite3
import os
from datetime import date
import google.generativeai as genai

render = web.template.render('avance_infante/views')

db_path = "sql/conaap.db"

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
modelo_ia = genai.GenerativeModel("gemini-flash-latest")


def generar_analisis_evolucion(evolucion, fechas_actividades, hechas_asignadas, total_asignadas):
    if not evolucion:
        return "Todavia no hay cuestionarios de desarrollo registrados para poder analizar la evolucion. En cuanto respondas el primero, aqui vera el analisis."

    resumen_resultados = "\n".join(
        f"- {fila['fecha']}: nivel de riesgo {fila['nivel_riesgo']}" for fila in evolucion
    )
    resumen_actividades = "\n".join(f"- {f}" for f in fechas_actividades) if fechas_actividades else "Sin actividades post-crisis registradas todavia."

    prompt = f"""Eres un asistente que apoya a padres de ninos con autismo en Mexico, en un programa de CONAFE.

Analiza la siguiente informacion y escribe un analisis extenso, claro y en espanol (entre 8 y 10 lineas),
explicando como ha ido evolucionando el desarrollo del nino desde el primer cuestionario, relacionando
especificamente las fechas de las actividades post-crisis con las fechas y niveles de riesgo de los
cuestionarios. Estructura el analisis asi:
1. Un resumen de donde empezo (primer resultado) y donde esta ahora (ultimo resultado).
2. Si la constancia en actividades coincide en el tiempo con cambios en el nivel de riesgo, mencionalo
   con cautela (sin asegurar causalidad directa, solo como una relacion observable).
3. Que puede esperar la familia si mantiene o aumenta esta constancia, mencionando areas concretas
   (regulacion emocional, comunicacion, manejo de rutinas, reduccion de crisis).
Si todavia no hay suficiente informacion para concluir una tendencia clara, dilo con honestidad en vez
de inventar una conclusion. No hagas diagnosticos medicos, mantén un tono calido y de acompanamiento.

Historial de cuestionarios (nivel de riesgo por fecha, del mas viejo al mas reciente):
{resumen_resultados}

Fechas en que se realizaron actividades post-crisis en casa:
{resumen_actividades}

Actividades asignadas por el docente completadas: {hechas_asignadas} de {total_asignadas}
"""
    try:
        respuesta = modelo_ia.generate_content(prompt)
        return respuesta.text
    except Exception as error:
        print("ERROR IA EVOLUCION: %s" % (error,))
        return "Con cada cuestionario y actividad que completas se construye un mejor panorama del desarrollo de tu hijo. Sigue apoyandolo con constancia."


class AvanceInfante:
    def GET(self):
        session = web.config._session
        id_infante = session.id_infante_actual

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT fecha, nivel_riesgo FROM resultados WHERE id_infante1 = ? ORDER BY fecha", (id_infante,))
        evolucion = cur.fetchall()

        cur.execute("SELECT COUNT(*) FROM actividad_postcrisis")
        total_act = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT COUNT(DISTINCT id_actividad) FROM actividad_postcrisis_realizada
            WHERE id_infante = ?
        """, (id_infante,))
        hechas_act = cur.fetchone()[0] or 0

        progreso_pct = round((hechas_act / total_act) * 100) if total_act > 0 else 0

        cur.execute("""
            SELECT COUNT(DISTINCT date(fecha)) FROM actividad_postcrisis_realizada
            WHERE id_infante = ?
        """, (id_infante,))
        dias_apoyando = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT DISTINCT date(fecha) AS fecha FROM actividad_postcrisis_realizada
            WHERE id_infante = ? ORDER BY fecha
        """, (id_infante,))
        fechas_actividades = [fila["fecha"] for fila in cur.fetchall()]

        cur.execute("""
            SELECT COUNT(*) AS total, SUM(CASE WHEN estado='Completada' THEN 1 ELSE 0 END) AS hechas
            FROM actividad_asignada WHERE id_infante = ?
        """, (id_infante,))
        fila_asig = cur.fetchone()
        total_asignadas = fila_asig["total"] or 0
        hechas_asignadas = fila_asig["hechas"] or 0

        hoy = str(date.today())

        cur.execute("SELECT texto, fecha FROM analisis_evolucion_ia WHERE id_infante = ?", (id_infante,))
        cache_analisis = cur.fetchone()
        if cache_analisis and cache_analisis["fecha"] == hoy:
            analisis_evolucion = cache_analisis["texto"]
        else:
            analisis_evolucion = generar_analisis_evolucion(evolucion, fechas_actividades, hechas_asignadas, total_asignadas)
            cur.execute("""
                INSERT INTO analisis_evolucion_ia (id_infante, texto, fecha) VALUES (?, ?, ?)
                ON CONFLICT(id_infante) DO UPDATE SET texto = excluded.texto, fecha = excluded.fecha
            """, (id_infante, analisis_evolucion, hoy))
            conn.commit()

        conn.close()

        return render.avance_infante(
            "avance", evolucion, progreso_pct, hechas_act, total_act,
            dias_apoyando, analisis_evolucion
        )