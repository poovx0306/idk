import web
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
