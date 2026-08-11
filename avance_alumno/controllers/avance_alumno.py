import web
import sqlite3
import re
import datetime
from ia_groq import generar_texto_ia

render = web.template.render('avance_alumno/views')

ETIQUETAS_SECCIONES = [
    ("AVANCE", "Avance en este tema"),
    ("SIGUIENTE", "Siguiente paso sugerido"),
]

SYSTEM_PROMPT = "Eres un asistente pedagógico que escribe en español neutro, claro y práctico para un docente, sin usar markdown ni asteriscos."


def obtener_docente(cursor, id_docente):
    cursor.execute("SELECT nombre, correo FROM docente WHERE id_docente = ?", (id_docente,))
    fila = cursor.fetchone()
    nombre = fila["nombre"] if fila else "Docente"
    correo = fila["correo"] if fila else "sin-correo@conafe.gob.mx"
    return nombre, correo


def _asegurar_tabla_analisis(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analisis_avance_docente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_infante INTEGER NOT NULL,
            id_tema INTEGER NOT NULL,
            texto TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    """)


def parsear_secciones(texto):
    if not texto:
        return None
    patron = re.compile(r'(?:^|\n)\s*(AVANCE|SIGUIENTE)\s*:\s*', re.IGNORECASE)
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


def generar_texto_reglas(intentos_asc, titulo_tema, materia):
    ultimo = intentos_asc[-1]
    if len(intentos_asc) >= 2:
        anterior = intentos_asc[-2]
        if ultimo["porcentaje"] > anterior["porcentaje"]:
            avance = f"Mejoró de {anterior['porcentaje']}% a {ultimo['porcentaje']}% de criterios logrados respecto al intento anterior."
        elif ultimo["porcentaje"] < anterior["porcentaje"]:
            avance = f"Bajó de {anterior['porcentaje']}% a {ultimo['porcentaje']}% de criterios logrados respecto al intento anterior."
        else:
            avance = f"Se mantuvo en {ultimo['porcentaje']}% de criterios logrados, igual que el intento anterior."
    else:
        avance = f"Esta es la primera evaluación registrada de este tema, con {ultimo['porcentaje']}% de criterios logrados."
    if ultimo["observaciones"]:
        avance += f" Observación registrada: \"{ultimo['observaciones']}\"."

    if ultimo["porcentaje"] == 100:
        siguiente = f"Dominó por completo \"{titulo_tema}\". Puede avanzar al siguiente tema de {materia} para seguir progresando académicamente."
    elif ultimo["porcentaje"] >= 50:
        siguiente = "Le falta consolidar algunos criterios. Repite el tema reforzando justo lo que señalan las observaciones del último intento antes de avanzar a un tema nuevo."
    elif len(intentos_asc) > 1:
        siguiente = "Sigue sin lograr la mayoría de los criterios después de varios intentos. Antes de repetirlo de nuevo, prueba ajustar el apoyo visual o dividir la actividad en pasos más pequeños."
    else:
        siguiente = "Logró pocos o ningún criterio. Se recomienda repetir el tema en otra sesión para poder comparar el avance."

    return f"AVANCE: {avance}\nSIGUIENTE: {siguiente}"


def construir_prompt(titulo_tema, materia, intentos_asc):
    resumen = "\n".join(
        f"- Intento {i+1} ({it['fecha']}): {it['logrados']} de {it['total']} criterios logrados ({it['porcentaje']}%). "
        f"Observación del docente: {it['observaciones'] or 'sin observaciones'}."
        for i, it in enumerate(intentos_asc)
    )
    return f"""Eres un asistente que ayuda a un docente de CONAFE a interpretar el avance de un alumno con autismo (TEA)
en un tema específico de la relación tutora 1 a 1.

Tema: {titulo_tema} ({materia})
Historial de evaluaciones de este alumno en este tema, en orden cronológico:
{resumen}

Responde ÚNICAMENTE en este formato exacto, con estas 2 etiquetas en mayúsculas y dos puntos, cada una en su propia línea,
sin agregar texto antes ni después, sin markdown ni asteriscos:

AVANCE: (2-3 líneas comparando el último intento contra los anteriores, mencionando específicamente qué mejoró o no)
SIGUIENTE: (2-3 líneas con una recomendación concreta y accionable para la próxima sesión: si no logró la mayoría de los criterios, sugiere repetir el tema y un ajuste puntual basado en las observaciones; si ya lo domina, sugiere avanzar al siguiente tema de la misma materia)

Sé honesto pero alentador, sin dar diagnósticos médicos."""


def generar_recomendacion(cursor, conexion, id_infante, id_tema, titulo_tema, materia, intentos_asc):
    hoy = str(datetime.date.today())
    _asegurar_tabla_analisis(cursor)
    cursor.execute(
        "SELECT texto FROM analisis_avance_docente WHERE id_infante = ? AND id_tema = ? AND fecha = ?",
        (id_infante, id_tema, hoy),
    )
    fila = cursor.fetchone()
    if fila and parsear_secciones(fila["texto"]):
        texto = fila["texto"]
    else:
        prompt = construir_prompt(titulo_tema, materia, intentos_asc)
        texto = generar_texto_ia(prompt, system=SYSTEM_PROMPT)
        if not texto or not parsear_secciones(texto):
            texto = generar_texto_reglas(intentos_asc, titulo_tema, materia)
        cursor.execute(
            "DELETE FROM analisis_avance_docente WHERE id_infante = ? AND id_tema = ? AND fecha = ?",
            (id_infante, id_tema, hoy),
        )
        cursor.execute(
            "INSERT INTO analisis_avance_docente (id_infante, id_tema, texto, fecha) VALUES (?, ?, ?, ?)",
            (id_infante, id_tema, texto, hoy),
        )
        conexion.commit()
    return parsear_secciones(texto) or [{"etiqueta": "Recomendación", "texto": texto}]


class AvanceAlumno:
    def GET(self):
        datos = web.input(id="1", id_alumno="")
        id_docente = datos.id
        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        nombre_docente, correo_docente = obtener_docente(cursor, id_docente)
        if not datos.id_alumno:
            cursor.execute(
                "SELECT id_infante, nombre FROM infantes WHERE id_docente1 = ? ORDER BY nombre",
                (id_docente,),
            )
            alumnos = cursor.fetchall()
            conexion.close()
            return render.avance_alumno_seleccion(id_docente, nombre_docente, correo_docente, alumnos)
        id_alumno = datos.id_alumno
        cursor.execute("SELECT nombre FROM infantes WHERE id_infante = ?", (id_alumno,))
        fila_alumno = cursor.fetchone()
        if not fila_alumno:
            conexion.close()
            raise web.notfound()
        nombre_alumno = fila_alumno["nombre"]
        cursor.execute("""
            SELECT r.id, r.id_tema, r.fecha, r.observaciones, t.titulo, t.materia
            FROM retroalimentacion r
            JOIN temas t ON t.id = r.id_tema
            WHERE r.id_infante = ?
            ORDER BY t.titulo, r.id ASC
        """, (id_alumno,))
        filas = cursor.fetchall()
        temas = {}
        orden_temas = []
        for fila in filas:
            id_tema = fila["id_tema"]
            if id_tema not in temas:
                cursor.execute("SELECT COUNT(*) FROM criterio_tema WHERE id_tema = ?", (id_tema,))
                total_criterios = cursor.fetchone()[0]
                temas[id_tema] = {
                    "titulo": fila["titulo"],
                    "materia": fila["materia"],
                    "total_criterios": total_criterios,
                    "intentos": [],
                }
                orden_temas.append(id_tema)
            cursor.execute(
                "SELECT COUNT(*) FROM retroalimentacion_criterio WHERE id_retroalimentacion = ? AND logrado = 1",
                (fila["id"],),
            )
            logrados = cursor.fetchone()[0]
            total = temas[id_tema]["total_criterios"]
            porcentaje = round((logrados / total) * 100) if total else 0
            temas[id_tema]["intentos"].append({
                "fecha": fila["fecha"],
                "observaciones": fila["observaciones"] or "",
                "logrados": logrados,
                "total": total,
                "porcentaje": porcentaje,
            })
        lista_temas = []
        for id_tema in orden_temas:
            info = temas[id_tema]
            intentos_asc = info["intentos"]
            ultimo = intentos_asc[-1]
            tendencia = "primera_vez"
            if len(intentos_asc) >= 2:
                anterior = intentos_asc[-2]
                if ultimo["porcentaje"] > anterior["porcentaje"]:
                    tendencia = "mejora"
                elif ultimo["porcentaje"] < anterior["porcentaje"]:
                    tendencia = "retroceso"
                else:
                    tendencia = "igual"
            secciones = generar_recomendacion(
                cursor, conexion, id_alumno, id_tema, info["titulo"], info["materia"], intentos_asc
            )
            lista_temas.append({
                "titulo": info["titulo"],
                "materia": info["materia"],
                "total_criterios": info["total_criterios"],
                "intentos": list(reversed(intentos_asc)),
                "num_intentos": len(intentos_asc),
                "tendencia": tendencia,
                "recomendacion": secciones,
            })
        conexion.close()
        return render.avance_alumno(
            id_docente, nombre_docente, correo_docente,
            nombre_alumno, id_alumno, lista_temas
        )
