"""
Corrige que la pagina de resultado siempre mostraba lo ultimo guardado en
localStorage del navegador, sin importar a cual resultado le dabas clic
(desde el historial, desde la alerta de "ya contestaste", o desde el banner
de inicio). Ahora, cuando se entra con ?id=<id_resultado> en la URL, se
consulta ese resultado exacto en la base de datos y se muestra ese.

IMPORTANTE: esto NO toca el calculo de puntaje ni los umbrales de riesgo.
- cuestionario.js: no se toca la suma de puntos (puntajeTotal), solo se
  cambia a donde redirige despues de guardar (ahora incluye el id).
- guardar_resultado.py: no se tocan los umbrales (>=35 Alto, >=18 Medio,
  si no Bajo), solo se agrega el id del registro insertado a la respuesta.

Cambios:
1. guardar_resultado.py -> devuelve el id_resultado insertado.
2. static/js/cuestionario.js -> redirige a /resultado?id=<id>.
3. resultado.py -> si viene ?id=, consulta ese resultado real en la BD.
4. resultado.html -> si el servidor mando el resultado real, lo usa en vez
   de localStorage.
5. seleccionar_nino.py -> la alerta de "ya contestado" tambien manda el id
   real del resultado guardado.
6. ya_contestado.html -> el boton "Ver resultado guardado" ya usa ese id.
7. inicio_padres.html -> el boton "Ver resultado" del banner tambien usa el
   id del resultado mas reciente.

Correr desde la raiz del repo: python3 corregir_resultado_real.py
"""
import os

RAIZ = os.getcwd()


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def escribir(ruta, contenido):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)


def reemplazar(ruta, viejo, nuevo, nombre_paso):
    if not os.path.exists(ruta):
        print(f"  [omitido] no existe: {ruta}")
        return
    contenido = leer(ruta)
    if nuevo.strip() and nuevo in contenido:
        print(f"  [sin cambios] {nombre_paso} ya estaba en {ruta}")
        return
    if viejo not in contenido:
        print(f"  [AVISO] no se encontro el bloque esperado para '{nombre_paso}' en {ruta}")
        return
    contenido = contenido.replace(viejo, nuevo, 1)
    escribir(ruta, contenido)
    print(f"  [ok] {nombre_paso} en {ruta}")


# =================================================================
# 1. guardar_resultado.py - devolver el id_resultado insertado
# =================================================================
print("== Reescribiendo deteccion_temprana/controllers/guardar_resultado.py ==")

NUEVO_GUARDAR = '''import web
import sqlite3
import json
from datetime import date
render = web.template.render('deteccion_temprana/views/')
class GuardarResultadoAPI:
    def POST(self):
        session = web.config._session
        id_infante = session.id_infante_actual
        web.header('Content-Type', 'application/json')
        if not id_infante:
            return json.dumps({"ok": False, "error": "no_hay_infante_seleccionado"})
        try:
            datos = json.loads(web.data())
            puntaje = int(datos.get("puntaje", 0))
        except Exception:
            return json.dumps({"ok": False, "error": "datos_invalidos"})
        print("DATOS RECIBIDOS:", datos)
        print("PUNTAJE CONVERTIDO:", puntaje)
        if puntaje >= 35:
            nivel_riesgo = "Alto"
        elif puntaje >= 18:
            nivel_riesgo = "Medio"
        else:
            nivel_riesgo = "Bajo"
        try:
            conn = sqlite3.connect("sql/conaap.db")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO resultados (puntaje, fecha, nivel_riesgo, numero_de_especialista, id_infante1) VALUES (?, ?, ?, ?, ?)",
                (puntaje, str(date.today()), nivel_riesgo, "Pendiente de asignar", id_infante)
            )
            id_resultado = cur.lastrowid
            conn.commit()
            conn.close()
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})
        return json.dumps({"ok": True, "id_resultado": id_resultado})
'''
ruta_guardar = os.path.join(RAIZ, "deteccion_temprana", "controllers", "guardar_resultado.py")
escribir(ruta_guardar, NUEVO_GUARDAR)
print(f"  [ok] reescrito: {ruta_guardar}")

# =================================================================
# 2. static/js/cuestionario.js - redirigir con el id
# =================================================================
print("== Editando static/js/cuestionario.js ==")
ruta_js = os.path.join(RAIZ, "static", "js", "cuestionario.js")

JS_VIEJO = '''    fetch('/api/guardar-resultado', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ puntaje: puntajeTotal })
    })
    .then(response => response.json())
    .then(data => {
        window.location.href = '/resultado';
    })
    .catch(error => {
        console.error("Error al guardar:", error);
        window.location.href = '/resultado';
    });'''
JS_NUEVO = '''    fetch('/api/guardar-resultado', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ puntaje: puntajeTotal })
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok && data.id_resultado) {
            window.location.href = '/resultado?id=' + data.id_resultado;
        } else {
            window.location.href = '/resultado';
        }
    })
    .catch(error => {
        console.error("Error al guardar:", error);
        window.location.href = '/resultado';
    });'''
reemplazar(ruta_js, JS_VIEJO, JS_NUEVO, "redirigir con id_resultado")

# =================================================================
# 3. resultado.py - leer ?id= y consultar la BD
# =================================================================
print("== Reescribiendo deteccion_temprana/controllers/resultado.py ==")

NUEVO_RESULTADO = '''import web
import sqlite3

render = web.template.render('deteccion_temprana/views/')


class Resultado:
    def GET(self):
        session = web.config._session
        origen = getattr(session, 'origen_cuestionario', None)
        if origen == 'publico':
            es_padre = False
        elif origen == 'padre':
            es_padre = True
        else:
            es_padre = getattr(session, 'rol', None) == 'padre'

        datos = web.input(id=None)
        hay_resultado_servidor = False
        puntaje_servidor = 0
        nivel_riesgo_servidor = ""
        if datos.id:
            conn = sqlite3.connect("sql/conaap.db")
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "SELECT puntaje, nivel_riesgo FROM resultados WHERE id_resultado = ?",
                (int(datos.id),),
            )
            fila = cur.fetchone()
            conn.close()
            if fila:
                hay_resultado_servidor = True
                puntaje_servidor = fila["puntaje"]
                nivel_riesgo_servidor = fila["nivel_riesgo"]

        return render.resultado(es_padre, hay_resultado_servidor, puntaje_servidor, nivel_riesgo_servidor)
'''
ruta_resultado = os.path.join(RAIZ, "deteccion_temprana", "controllers", "resultado.py")
escribir(ruta_resultado, NUEVO_RESULTADO)
print(f"  [ok] reescrito: {ruta_resultado}")

# =================================================================
# 4. resultado.html - usar el resultado real cuando venga del servidor
# =================================================================
print("== Editando deteccion_temprana/views/resultado.html ==")
ruta_resultado_html = os.path.join(RAIZ, "deteccion_temprana", "views", "resultado.html")

DEF_VIEJO = "$def with (es_padre)"
DEF_NUEVO = "$def with (es_padre, hay_resultado_servidor, puntaje_servidor, nivel_riesgo_servidor)"
reemplazar(ruta_resultado_html, DEF_VIEJO, DEF_NUEVO, "$def with")

SCRIPT_VIEJO = '''<script>
    document.addEventListener("DOMContentLoaded", function() {
        var dataRaw = localStorage.getItem('veanme_resultado');
        var puntaje = 0;

        if (dataRaw) {
            var data = JSON.parse(dataRaw);
            puntaje = data.puntajeTotal || 0;
        }

        var imgSemaforo = document.getElementById('img-semaforo');'''
SCRIPT_NUEVO = '''<script>
    $if hay_resultado_servidor:
        var HAY_RESULTADO_SERVIDOR = true;
        var PUNTAJE_SERVIDOR = $puntaje_servidor;
    $else:
        var HAY_RESULTADO_SERVIDOR = false;
        var PUNTAJE_SERVIDOR = null;

    document.addEventListener("DOMContentLoaded", function() {
        var data = null;
        var puntaje = 0;

        if (HAY_RESULTADO_SERVIDOR) {
            puntaje = PUNTAJE_SERVIDOR;
        } else {
            var dataRaw = localStorage.getItem('veanme_resultado');
            if (dataRaw) {
                data = JSON.parse(dataRaw);
                puntaje = data.puntajeTotal || 0;
            }
        }

        var imgSemaforo = document.getElementById('img-semaforo');'''
reemplazar(ruta_resultado_html, SCRIPT_VIEJO, SCRIPT_NUEVO, "usar resultado real del servidor si viene por id")

# =================================================================
# 5. seleccionar_nino.py - incluir id_resultado en la alerta de "ya contestado"
# =================================================================
print("== Reescribiendo deteccion_temprana/controllers/seleccionar_nino.py ==")

NUEVO_SELECCIONAR = '''import web
import sqlite3
from datetime import date

render = web.template.render('deteccion_temprana/views/')


class SeleccionarNino:
    def GET(self):
        session = web.config._session
        id_padres = session.id_referencia
        datos = web.input(destino='inicio')
        conn = sqlite3.connect("sql/conaap.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id_infante, nombre, edad FROM infantes WHERE id_padres = ?", (id_padres,))
        ninos = cur.fetchall()
        conn.close()
        return render.seleccionar_nino(ninos, datos.destino)


class ElegirNino:
    def GET(self):
        session = web.config._session
        datos = web.input(id_infante=None, destino='inicio', forzar=None)
        id_infante = int(datos.id_infante)
        session.id_infante_actual = id_infante

        if datos.destino == 'cuestionario':
            session.origen_cuestionario = 'padre'
            if datos.forzar == '1':
                raise web.HTTPError('303 See Other', {'Location': '/cuestionario'})

            conn = sqlite3.connect("sql/conaap.db")
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "SELECT id_resultado, nivel_riesgo, fecha FROM resultados WHERE id_infante1 = ? ORDER BY id_resultado DESC LIMIT 1",
                (id_infante,),
            )
            ya_contestado = cur.fetchone()
            cur.execute("SELECT nombre FROM infantes WHERE id_infante = ?", (id_infante,))
            infante = cur.fetchone()
            conn.close()

            if ya_contestado:
                nombre_infante = infante["nombre"] if infante else "este niño"
                return render.ya_contestado(
                    nombre_infante, ya_contestado["nivel_riesgo"], ya_contestado["fecha"],
                    id_infante, ya_contestado["id_resultado"]
                )

            raise web.HTTPError('303 See Other', {'Location': '/cuestionario'})
        else:
            raise web.HTTPError('303 See Other', {'Location': '/padre/inicio'})
'''
ruta_seleccionar = os.path.join(RAIZ, "deteccion_temprana", "controllers", "seleccionar_nino.py")
escribir(ruta_seleccionar, NUEVO_SELECCIONAR)
print(f"  [ok] reescrito: {ruta_seleccionar}")

# =================================================================
# 6. ya_contestado.html - usar el id real en "Ver resultado guardado"
# =================================================================
print("== Editando deteccion_temprana/views/ya_contestado.html ==")
ruta_ya_contestado = os.path.join(RAIZ, "deteccion_temprana", "views", "ya_contestado.html")

DEF_YA_VIEJO = "$def with (nombre_infante, nivel_riesgo, fecha, id_infante)"
DEF_YA_NUEVO = "$def with (nombre_infante, nivel_riesgo, fecha, id_infante, id_resultado)"
reemplazar(ruta_ya_contestado, DEF_YA_VIEJO, DEF_YA_NUEVO, "$def with")

LINK_YA_NUEVO = '<a class="btn-primary" href="/resultado?id=$id_resultado">Ver resultado guardado</a>'
LINK_YA_VIEJO_A = '<a class="btn-primary" href="/resultado">Ver resultado de hoy</a>'
LINK_YA_VIEJO_B = '<a class="btn-primary" href="/resultado">Ver resultado guardado</a>'
contenido_ya = leer(ruta_ya_contestado) if os.path.exists(ruta_ya_contestado) else ""
if LINK_YA_NUEVO in contenido_ya:
    print(f"  [sin cambios] link con id_resultado ya estaba en {ruta_ya_contestado}")
elif LINK_YA_VIEJO_B in contenido_ya:
    reemplazar(ruta_ya_contestado, LINK_YA_VIEJO_B, LINK_YA_NUEVO, "link con id_resultado")
elif LINK_YA_VIEJO_A in contenido_ya:
    reemplazar(ruta_ya_contestado, LINK_YA_VIEJO_A, LINK_YA_NUEVO, "link con id_resultado")
else:
    print(f"  [AVISO] no se encontro el link esperado de 'Ver resultado' en {ruta_ya_contestado}")

# =================================================================
# 7. inicio_padres.html - el boton del banner tambien manda el id real
# =================================================================
print("== Editando inicio_padres/views/inicio_padres.html ==")
ruta_inicio_padres = os.path.join(RAIZ, "inicio_padres", "views", "inicio_padres.html")

if os.path.exists(ruta_inicio_padres):
    contenido = leer(ruta_inicio_padres)
    viejo_link = '''<a href="/resultado" class="banner-btn">Ver resultado</a>'''
    nuevo_link = '''<a href="/resultado?id=$historial[0]['id_resultado']" class="banner-btn">Ver resultado</a>'''
    ocurrencias = contenido.count(viejo_link)
    if ocurrencias:
        contenido = contenido.replace(viejo_link, nuevo_link)
        escribir(ruta_inicio_padres, contenido)
        print(f"  [ok] {ocurrencias} enlace(s) 'Ver resultado' actualizados en {ruta_inicio_padres}")
    elif nuevo_link in contenido:
        print(f"  [sin cambios] ya estaba en {ruta_inicio_padres}")
    else:
        print(f"  [AVISO] no se encontro el link esperado en {ruta_inicio_padres}")
else:
    print(f"  [omitido] no existe: {ruta_inicio_padres}")

print("\\nListo. Si salio algun [AVISO], pega aqui esa parte del archivo para ajustarlo a mano.")
print("Prueba: entra al historial reciente o dale 'Ver resultado' en el banner de inicio, y confirma que")
print("muestra el semaforo y nivel de riesgo que de verdad corresponde a ese resultado, no el ultimo que")
print("contestaste en el navegador.")