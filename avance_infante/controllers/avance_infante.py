import web
import sqlite3
import re
import datetime
from ia_groq import generar_texto_ia

render = web.template.render('avance_infante/views')
db_path = "sql/conaap.db"

ORDEN_RIESGO = {"Bajo": 0, "Medio": 1, "Alto": 2}

ETIQUETAS_SECCIONES = [
    ("PROGRESO", "Progreso académico"),
    ("FORTALEZAS", "Fortalezas"),
    ("REFORZAR", "En qué reforzar"),
    ("CASA", "Cómo ayudar en casa"),
]

SYSTEM_PROMPT = "Eres un asistente pedagógico que escribe en español neutro, claro y cálido para padres de familia, sin usar markdown ni asteriscos."


def parsear_secciones(texto):
    if not texto:
        return None
    patron = re.compile(r'(?:^|\n)\s*(PROGRESO|FORTALEZAS|REFORZAR|CASA)\s*:\s*', re.IGNORECASE)
    piezas = patron.split(texto)
    if len(piezas) < 3:
        return None
    mapa = {}
    for i in range(1, len(piezas), 2):
        clave = piezas[i].strip().upper()
        valor = piezas[i + 1].strip() if i + 1 < len(piezas) else ""
        if valor:
            mapa[clave] = valor
    secciones = []
    for clave, etiqueta in ETIQUETAS_SECCIONES:
        if clave in mapa:
            secciones.append({"etiqueta": etiqueta, "texto": mapa[clave]})
    return secciones if len(secciones) >= 2 else None


def generar_texto_reglas(evolucion, resumen_temas, actividades_casa_hechas, total_casa):
    if len(evolucion) >= 2:
        anterior, ultimo = evolucion[-2]["nivel_riesgo"], evolucion[-1]["nivel_riesgo"]
        if ORDEN_RIESGO.get(ultimo, 1) < ORDEN_RIESGO.get(anterior, 1):
            progreso = f"El nivel de riesgo bajó de {anterior} a {ultimo} entre los dos últimos cuestionarios, lo cual es una señal positiva de progreso."
        elif ORDEN_RIESGO.get(ultimo, 1) > ORDEN_RIESGO.get(anterior, 1):
            progreso = f"El nivel de riesgo subió de {anterior} a {ultimo} entre los dos últimos cuestionarios. Esto no significa un retroceso definitivo, pero conviene estar más atentos en las próximas semanas."
        else:
            progreso = f"El nivel de riesgo se mantiene en {ultimo}, igual que en el cuestionario anterior."
    elif len(evolucion) == 1:
        progreso = f"Hasta ahora solo hay un cuestionario respondido, con nivel de riesgo {evolucion[-1]['nivel_riesgo']}. Con un segundo cuestionario podremos comparar la evolución."
    else:
        progreso = "Todavía no hay cuestionarios respondidos."

    total_temas = len(resumen_temas)
    dominados = [t for t in resumen_temas if t["total"] > 0 and t["logrados"] == t["total"]]
    if total_temas > 0:
        progreso += f" En clase, el maestro ha evaluado {total_temas} tema(s) y en {len(dominados)} de ellos se lograron todos los criterios."

    if dominados:
        nombres = ", ".join(t["titulo"] for t in dominados)
        fortalezas = f"Domina por completo: {nombres}. Esto muestra que, cuando el tema se trabaja paso a paso, logra consolidarlo del todo."
    else:
        fortalezas = "Todavía no hay un tema dominado al 100%, pero cada evaluación del maestro ayuda a identificar exactamente en qué va avanzando."

    pendientes = [t for t in resumen_temas if t["total"] > 0 and t["logrados"] < t["total"]]
    if pendientes:
        peor = min(pendientes, key=lambda t: t["logrados"] / t["total"])
        reforzar = (f"El tema donde más le cuesta trabajo es \"{peor['titulo']}\" "
                    f"({peor['logrados']} de {peor['total']} criterios logrados). "
                    f"Repasar este tema con calma ayuda a que las bases queden firmes antes de avanzar a temas más complejos.")
    elif total_temas > 0:
        reforzar = "Por ahora no hay temas pendientes por reforzar: todos los evaluados están dominados. Se puede seguir avanzando a temas nuevos."
    else:
        reforzar = "Todavía no hay evaluaciones de temas para saber qué reforzar."

    if total_casa > 0:
        proporcion = actividades_casa_hechas / total_casa
        if proporcion < 0.5:
            casa = (f"Se han realizado {actividades_casa_hechas} de {total_casa} actividades sugeridas para casa. "
                    "Practicar en casa lo que se ve en clase ayuda a que el aprendizaje se refuerce y avance más rápido; "
                    "intenta apartar unos minutos al día para retomar alguna de las actividades pendientes.")
        else:
            casa = (f"¡Buen ritmo! Ya se realizaron {actividades_casa_hechas} de {total_casa} actividades en casa. "
                    "Mantener esta constancia es una de las mejores formas de acompañar su progreso académico.")
    else:
        casa = "Todavía no hay actividades para casa registradas."

    return f"PROGRESO: {progreso}\nFORTALEZAS: {fortalezas}\nREFORZAR: {reforzar}\nCASA: {casa}"


def construir_prompt(evolucion, resumen_temas, actividades_casa_hechas, total_casa):
    resumen_resultados = "\n".join(
        f"- {r['fecha']}: nivel de riesgo {r['nivel_riesgo']}" for r in evolucion
    ) or "No hay cuestionarios respondidos todavía."
    resumen_temas_txt = "\n".join(
        f"- {t['titulo']}: {t['logrados']} de {t['total']} criterios logrados"
        for t in resumen_temas
    ) or "Todavía no hay evaluaciones de temas registradas por el maestro."

    return f"""Eres un asistente que ayuda a padres de niños con autismo (TEA) a entender el progreso académico de su hijo.

Datos disponibles:
- Historial de niveles de riesgo por cuestionario (en orden cronológico):
{resumen_resultados}
- Evaluaciones que el maestro ha registrado en clase, por tema trabajado (último intento de cada tema):
{resumen_temas_txt}
- Actividades en casa: {actividades_casa_hechas} realizadas de {total_casa} disponibles.

Responde ÚNICAMENTE en este formato exacto, con estas 4 etiquetas en mayúsculas y dos puntos, cada una en su propia línea,
sin agregar texto antes ni después, sin usar markdown ni asteriscos:

PROGRESO: (3-4 líneas explicando en qué ha mejorado o no el niño, comparando el nivel de riesgo con lo que el maestro registró en clase)
FORTALEZAS: (2-3 líneas mencionando específicamente en qué temas le está yendo bien y por qué eso ayuda a su desarrollo)
REFORZAR: (2-3 líneas mencionando el tema específico donde más necesita apoyo y una razón concreta de cómo reforzarlo ayuda a su progreso académico)
CASA: (2-3 líneas con una recomendación concreta y accionable sobre las actividades en casa, explicando cómo eso ayuda a que progrese académicamente)

Sé cálido, honesto y alentador, sin dar diagnósticos médicos. Dirígete directamente al padre o madre."""


def generar_analisis(id_infante, evolucion, resumen_temas, actividades_casa_hechas, total_casa):
    hoy = str(datetime.date.today())
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT texto FROM analisis_evolucion_ia WHERE id_infante = ? AND fecha = ?",
        (id_infante, hoy)
    )
    fila = cur.fetchone()
    if fila and parsear_secciones(fila["texto"]):
        texto = fila["texto"]
    else:
        prompt = construir_prompt(evolucion, resumen_temas, actividades_casa_hechas, total_casa)
        texto = generar_texto_ia(prompt, system=SYSTEM_PROMPT)
        if not texto or not parsear_secciones(texto):
            texto = generar_texto_reglas(evolucion, resumen_temas, actividades_casa_hechas, total_casa)
        cur.execute("DELETE FROM analisis_evolucion_ia WHERE id_infante = ? AND fecha = ?", (id_infante, hoy))
        cur.execute(
            "INSERT INTO analisis_evolucion_ia (id_infante, texto, fecha) VALUES (?, ?, ?)",
            (id_infante, texto, hoy)
        )
        conn.commit()
    conn.close()
    return parsear_secciones(texto) or [{"etiqueta": "Análisis", "texto": texto}]


class AvanceInfante:
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
            return render.avance_infante_seleccion("avance", ninos)

        id_infante = int(datos.id_infante)
        cur.execute("SELECT nombre FROM infantes WHERE id_infante = ?", (id_infante,))
        infante = cur.fetchone()
        nombre_infante = infante["nombre"] if infante else ""

        cur.execute("SELECT fecha, nivel_riesgo FROM resultados WHERE id_infante1 = ? ORDER BY fecha", (id_infante,))
        evolucion = cur.fetchall()
        total_cuestionarios = len(evolucion)

        cur.execute("""
            SELECT r.id_tema, r.id, t.titulo
            FROM retroalimentacion r
            JOIN temas t ON t.id = r.id_tema
            WHERE r.id_infante = ?
            AND r.id = (
                SELECT MAX(r2.id) FROM retroalimentacion r2
                WHERE r2.id_infante = r.id_infante AND r2.id_tema = r.id_tema
            )
        """, (id_infante,))
        ultimos_temas = cur.fetchall()
        total_temas_evaluados = len(ultimos_temas)
        temas_dominados = 0
        resumen_temas = []
        for u in ultimos_temas:
            cur.execute("SELECT COUNT(*) FROM criterio_tema WHERE id_tema = ?", (u["id_tema"],))
            total_criterios = cur.fetchone()[0]
            cur.execute(
                "SELECT COUNT(*) FROM retroalimentacion_criterio WHERE id_retroalimentacion = ? AND logrado = 1",
                (u["id"],),
            )
            logrados = cur.fetchone()[0]
            if total_criterios > 0 and logrados == total_criterios:
                temas_dominados += 1
            resumen_temas.append({"titulo": u["titulo"], "logrados": logrados, "total": total_criterios})

        progreso_pct = round((temas_dominados / total_temas_evaluados) * 100) if total_temas_evaluados > 0 else 0

        cur.execute("SELECT COUNT(*) AS total FROM actividad_casa_realizada WHERE id_infante = ?", (id_infante,))
        actividades_casa_hechas = cur.fetchone()["total"] or 0
        cur.execute("SELECT COUNT(*) FROM actividad_casa")
        total_casa = cur.fetchone()[0]

        conn.close()

        respondio_cuestionario = total_cuestionarios > 0
        hay_evaluaciones = total_temas_evaluados > 0

        if not respondio_cuestionario and not hay_evaluaciones:
            secciones_analisis = [{"etiqueta": "Análisis", "texto": "Contesta el cuestionario y espera a que tu maestro registre evaluaciones de los temas trabajados en clase para que podamos darte un análisis del avance."}]
        elif respondio_cuestionario and not hay_evaluaciones:
            secciones_analisis = [{"etiqueta": "Análisis", "texto": "En cuanto tu maestro registre evaluaciones de los temas trabajados en clase, podremos darte un análisis completo del avance."}]
        elif not respondio_cuestionario and hay_evaluaciones:
            secciones_analisis = [{"etiqueta": "Análisis", "texto": "Contesta el cuestionario para que podamos darte un análisis completo del avance."}]
        else:
            secciones_analisis = generar_analisis(id_infante, evolucion, resumen_temas, actividades_casa_hechas, total_casa)

        return render.avance_infante(
            "avance", nombre_infante, total_cuestionarios, progreso_pct,
            temas_dominados, total_temas_evaluados, actividades_casa_hechas, total_casa, secciones_analisis
        )
