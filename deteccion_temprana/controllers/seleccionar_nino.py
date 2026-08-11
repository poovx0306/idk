import web
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
