import web
import sqlite3
import os
from datetime import date
import google.generativeai as genai

render = web.template.render('avance_infante/views')

db_path = "sql/conaap.db"

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
modelo_ia = genai.GenerativeModel("gemini-flash-latest")


def generar_prediccion(hechas_act, total_act, evolucion):
    niveles = [fila["nivel_riesgo"] for fila in evolucion]
    resumen_niveles = ", ".join(niveles) if niveles else "sin cuestionarios registrados todavia"

    prompt = f"""Eres un asistente que apoya a padres de ninos con autismo en Mexico, dentro de un programa de CONAFE.
Con base en estos datos, escribe un parrafo breve (maximo 4 lineas), calido y realista, en espanol,
explicando que mejoras puede esperar el padre si sigue apoyando a su hijo con las actividades.
No hagas diagnosticos medicos ni promesas exageradas, solo menciona beneficios generales y realistas
basados en constancia y apoyo familiar.

Datos:
- Actividades post-crisis completadas: {hechas_act} de {total_act}
- Evolucion de los cuestionarios de desarrollo (del mas viejo al mas reciente): {resumen_niveles}
"""
    try:
        respuesta = modelo_ia.generate_content(prompt)
        return respuesta.text
    except Exception as error:
        print("ERROR IA: %s" % (error,))
        return "Sigue apoyando a tu hijo con las actividades diarias; la constancia y el acompañamiento en casa hacen una gran diferencia en su desarrollo."


def generar_analisis_evolucion(evolucion, fechas_actividades, hechas_asignadas, total_asignadas):
    if not evolucion:
        return "Todavia no hay cuestionarios de desarrollo registrados para poder analizar la evolucion. En cuanto respondas el primero, aqui vera el analisis."

    resumen_resultados = "\n".join(
        f"- {fila['fecha']}: nivel de riesgo {fila['nivel_riesgo']}" for fila in evolucion
    )
    resumen_actividades = "\n".join(f"- {f}" for f in fechas_actividades) if fechas_actividades else "Sin actividades post-crisis registradas todavia."

    prompt = f"""Eres un asistente que apoya a padres de ninos con autismo en Mexico, en un programa de CONAFE.
Analiza la siguiente informacion y escribe un parrafo breve (maximo 5 lineas), claro y en espanol,
explicando como ha ido evolucionando el desarrollo del nino desde el primer cuestionario, relacionandolo
con la constancia en las actividades que ha hecho la familia. Si hay mejora, dilo con cautela; si no hay
suficiente informacion todavia para concluir algo, dilo tambien con honestidad. No hagas diagnosticos
medicos, solo un analisis de tendencia general y de acompanamiento, con tono calido.

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

        cur.execute("SELECT texto, fecha FROM prediccion_ia WHERE id_infante = ?", (id_infante,))
        cache_prediccion = cur.fetchone()
        if cache_prediccion and cache_prediccion["fecha"] == hoy:
            prediccion = cache_prediccion["texto"]
        else:
            prediccion = generar_prediccion(hechas_act, total_act, evolucion)
            cur.execute("""
                INSERT INTO prediccion_ia (id_infante, texto, fecha) VALUES (?, ?, ?)
                ON CONFLICT(id_infante) DO UPDATE SET texto = excluded.texto, fecha = excluded.fecha
            """, (id_infante, prediccion, hoy))
            conn.commit()

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
            dias_apoyando, prediccion, analisis_evolucion
        )