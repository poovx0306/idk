"""
Evita que se duplique el cuestionario del mismo dia para el mismo nino.

Como funciona el flujo actual:
  seleccionar-nino -> elegir-nino (guarda id_infante_actual en sesion y
  redirige a /cuestionario si destino='cuestionario') -> /cuestionario
  (DeteccionTemprana.GET, solo pinta la pagina) -> el JS
  (static/js/cuestionario.js) hace fetch a /api/guardar-resultado, que
  inserta en la tabla "resultados" usando session.id_infante_actual.

El lugar correcto para frenar la duplicacion es ElegirNino.GET: justo antes
de redirigir a /cuestionario, revisa si ya existe un resultado de HOY para
ese nino. Si ya existe, en vez de mandarlo al cuestionario le muestra una
alerta con el nivel de riesgo que ya obtuvo hoy y un boton para ver el
resultado completo, en vez de dejarlo contestar de nuevo y duplicar el
registro.

Si el nino contesto en un dia anterior (no hoy), no se bloquea: retomar el
cuestionario en otro dia sigue funcionando igual que ahora.

Correr desde la raiz del repo: python3 alerta_cuestionario_repetido.py
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
# 1. deteccion_temprana/controllers/seleccionar_nino.py - reescritura completa
# =================================================================
print("== Reescribiendo deteccion_temprana/controllers/seleccionar_nino.py ==")

NUEVO_CONTROLLER = '''import web
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
            if datos.forzar == '1':
                raise web.HTTPError('303 See Other', {'Location': '/cuestionario'})

            conn = sqlite3.connect("sql/conaap.db")
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "SELECT nivel_riesgo, fecha FROM resultados WHERE id_infante1 = ? ORDER BY id_resultado DESC LIMIT 1",
                (id_infante,),
            )
            ya_contestado = cur.fetchone()
            cur.execute("SELECT nombre FROM infantes WHERE id_infante = ?", (id_infante,))
            infante = cur.fetchone()
            conn.close()

            if ya_contestado:
                nombre_infante = infante["nombre"] if infante else "este niño"
                return render.ya_contestado(nombre_infante, ya_contestado["nivel_riesgo"], ya_contestado["fecha"], id_infante)

            raise web.HTTPError('303 See Other', {'Location': '/cuestionario'})
        else:
            raise web.HTTPError('303 See Other', {'Location': '/padre/inicio'})
'''
ruta_controller = os.path.join(RAIZ, "deteccion_temprana", "controllers", "seleccionar_nino.py")
escribir(ruta_controller, NUEVO_CONTROLLER)
print(f"  [ok] reescrito: {ruta_controller}")

# =================================================================
# 2. deteccion_temprana/views/ya_contestado.html - vista nueva
# =================================================================
print("== Creando deteccion_temprana/views/ya_contestado.html ==")

NUEVA_VISTA = '''$def with (nombre_infante, nivel_riesgo, fecha, id_infante)

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>CONAAP - Cuestionario ya contestado</title>
    <style>
        body { font-family: Arial, Helvetica, sans-serif; background: #6a1c32; min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }
        .card { background: #fff; border-radius: 20px; padding: 40px; width: 100%; max-width: 420px; text-align: center; }
        .icono { width: 56px; height: 56px; border-radius: 50%; background: #fef3c7; color: #92400e; display: flex; align-items: center; justify-content: center; font-size: 26px; margin: 0 auto 18px; }
        h1 { font-size: 19px; color: #1e293b; margin-bottom: 10px; }
        p { font-size: 13.5px; color: #64748b; line-height: 1.6; margin-bottom: 6px; }
        .nivel-badge { display: inline-block; margin: 14px 0 20px; font-size: 13px; font-weight: 700; padding: 7px 16px; border-radius: 20px; }
        .nivel-Alto { background: #fee2e2; color: #b91c1c; }
        .nivel-Medio { background: #fef3c7; color: #92400e; }
        .nivel-Bajo { background: #d1fae5; color: #065f46; }
        .btn-primary { display: block; background: #7e1232; color: #fff; text-decoration: none; padding: 12px; border-radius: 10px; font-weight: 700; font-size: 14px; margin-bottom: 10px; }
        .btn-secundario { display: block; background: #f1f5f9; color: #1e293b; text-decoration: none; padding: 12px; border-radius: 10px; font-weight: 600; font-size: 14px; margin-bottom: 10px; }
        .btn-forzar { display: block; background: none; color: #94a3b8; text-decoration: underline; padding: 4px; font-size: 12.5px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="icono">&#9888;</div>
        <h1>Ya contestaste este cuestionario</h1>
        <p>$nombre_infante ya tiene un cuestionario registrado (el $fecha). Revisa el resultado que ya se guardó antes de contestar otro.</p>
        <span class="nivel-badge nivel-$nivel_riesgo">Nivel de riesgo: $nivel_riesgo</span>
        <a class="btn-primary" href="/resultado">Ver resultado guardado</a>
        <a class="btn-secundario" href="/padre/inicio">Volver al inicio</a>
        <a class="btn-forzar" href="/padre/elegir-nino?id_infante=$id_infante&destino=cuestionario&forzar=1">Contestar de nuevo de todas formas</a>
    </div>
</body>
</html>
'''
ruta_vista = os.path.join(RAIZ, "deteccion_temprana", "views", "ya_contestado.html")
escribir(ruta_vista, NUEVA_VISTA)
print(f"  [ok] creado: {ruta_vista}")

print("\\nListo. Prueba: contesta un cuestionario con un niño, y luego intenta contestarlo otra vez con el mismo")
print("niño el mismo día -> debe salir la alerta en vez de dejarte contestar de nuevo.")