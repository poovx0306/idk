import web
import sqlite3
import re
import datetime
from ia_groq import generar_texto_ia

render = web.template.render('actividades_postcrisis/views')
db_path = "sql/conaap.db"

ETIQUETAS_CRISIS = [
    ("ENTENDER", "Qué pudo estar pasando"),
    ("AHORA", "Qué hacer en este momento"),
    ("DESPUES", "Cómo ayudar después"),
    ("PREVENIR", "Cómo prevenir la próxima vez"),
]

SYSTEM_PROMPT_CRISIS = "Eres un asistente pedagógico que escribe en español neutro, claro, cálido y práctico para padres de familia, sin usar markdown ni asteriscos."


def _asegurar_tabla_crisis(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crisis_registro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_infante INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            recomendaciones TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    """)


def parsear_recomendaciones(texto):
    if not texto:
        return None
    patron = re.compile(r'(?:^|\n)\s*(ENTENDER|AHORA|DESPUES|PREVENIR)\s*:\s*', re.IGNORECASE)
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
    for clave, etiqueta in ETIQUETAS_CRISIS:
        if clave in mapa:
            secciones.append({"etiqueta": etiqueta, "texto": mapa[clave]})
    return secciones if len(secciones) >= 2 else None


def generar_texto_reglas_crisis(nombre, descripcion):
    entender = ("Cada crisis o \"meltdown\" suele ser una respuesta a que algo resultó abrumador (ruido, cambio de "
                "rutina, cansancio, frustración, un cambio inesperado, etc.), no un berrinche intencional. Vale la "
                "pena identificar qué pasó justo antes para reconocer el detonante la próxima vez.")
    ahora = (f"Mantén la calma y baja tu propio tono de voz. Lleva a {nombre} a un espacio con menos estímulos "
             "(menos ruido, menos luz, menos gente). No le exijas hablar o explicarse en ese momento; dale espacio "
             "y tiempo para regularse, sin forzar el contacto físico si no lo busca.")
    despues = (f"Cuando {nombre} esté más tranquilo, retoma la actividad o rutina de forma gradual y sin presión. "
               "Una actividad sensorial suave (por ejemplo, algo con presión profunda, o un objeto familiar) puede "
               "ayudarle a terminar de regularse antes de continuar con el día.")
    prevenir = ("Anota la hora, el lugar y lo que pasó justo antes de la crisis; con varios registros como este "
                "podrán identificar un patrón de detonantes y anticiparse, por ejemplo avisando con tiempo los "
                "cambios de rutina o llevando algo que le tranquilice a los lugares donde suele costarle más.")
    return f"ENTENDER: {entender}\nAHORA: {ahora}\nDESPUES: {despues}\nPREVENIR: {prevenir}"


def construir_prompt_crisis(nombre, edad, condicion, descripcion):
    return f"""Eres un asistente que ayuda a padres de niños con autismo (TEA) a manejar crisis o "meltdowns".

Niño o niña: {nombre}, {edad} años. Condición: {condicion or 'TEA'}.
Descripción de lo que pasó en la crisis, escrita por el padre o madre:
"{descripcion}"

Responde ÚNICAMENTE en este formato exacto, con estas 4 etiquetas en mayúsculas y dos puntos, cada una en su propia línea,
sin agregar texto antes ni después, sin markdown ni asteriscos:

ENTENDER: (2-3 líneas explicando, según lo descrito, qué pudo haber causado o detonado la crisis)
AHORA: (2-3 líneas con pasos concretos y prácticos de qué hacer en este momento para ayudar a que se calme)
DESPUES: (2-3 líneas con qué hacer una vez que ya se calmó, incluyendo alguna actividad específica y breve)
PREVENIR: (2-3 líneas con una recomendación concreta para reducir el riesgo de que se repita una crisis similar)

Sé cálido, práctico y específico según lo que describió el padre. No des diagnósticos médicos."""


def generar_recomendaciones_crisis(nombre, edad, condicion, descripcion):
    prompt = construir_prompt_crisis(nombre, edad, condicion, descripcion)
    texto = generar_texto_ia(prompt, system=SYSTEM_PROMPT_CRISIS)
    if not texto or not parsear_recomendaciones(texto):
        texto = generar_texto_reglas_crisis(nombre, descripcion)
    return texto


class ActividadesPostcrisis:
    def GET(self):
        session = web.config._session
        id_padres = session.id_referencia
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        _asegurar_tabla_crisis(cur)

        cur.execute(
            "SELECT id_infante, nombre, edad, condicion FROM infantes WHERE id_padres = ? ORDER BY nombre",
            (id_padres,),
        )
        ninos = cur.fetchall()

        cur.execute("""
            SELECT c.id, c.descripcion, c.recomendaciones, c.fecha, i.nombre AS nombre_infante
            FROM crisis_registro c
            JOIN infantes i ON i.id_infante = c.id_infante
            WHERE i.id_padres = ?
            ORDER BY c.id DESC
            LIMIT 10
        """, (id_padres,))
        filas_historial = cur.fetchall()
        conn.close()

        historial = []
        for h in filas_historial:
            secciones = parsear_recomendaciones(h["recomendaciones"]) or [{"etiqueta": "Recomendación", "texto": h["recomendaciones"]}]
            historial.append({
                "nombre_infante": h["nombre_infante"],
                "descripcion": h["descripcion"],
                "fecha": h["fecha"],
                "recomendaciones": secciones,
            })

        return render.actividades_postcrisis("postcrisis", ninos, historial)


class RegistrarCrisis:
    def POST(self):
        session = web.config._session
        id_padres = session.id_referencia
        datos = web.input(id_infante=None, descripcion="")
        descripcion = datos.descripcion.strip()

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        _asegurar_tabla_crisis(cur)

        infante = None
        if datos.id_infante:
            cur.execute(
                "SELECT id_infante, nombre, edad, condicion FROM infantes WHERE id_infante = ? AND id_padres = ?",
                (int(datos.id_infante), id_padres),
            )
            infante = cur.fetchone()

        if not infante or not descripcion:
            conn.close()
            raise web.HTTPError('303 See Other', {'Location': '/padre/postcrisis'})

        recomendaciones = generar_recomendaciones_crisis(
            infante["nombre"], infante["edad"], infante["condicion"], descripcion
        )
        ahora = str(datetime.datetime.now())
        cur.execute(
            "INSERT INTO crisis_registro (id_infante, descripcion, recomendaciones, fecha) VALUES (?, ?, ?, ?)",
            (infante["id_infante"], descripcion, recomendaciones, ahora),
        )
        conn.commit()
        conn.close()
        raise web.HTTPError('303 See Other', {'Location': '/padre/postcrisis'})
