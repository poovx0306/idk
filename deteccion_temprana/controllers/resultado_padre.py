import web
import sqlite3

render = web.template.render('deteccion_temprana/views/')


class ResultadoPadre:
    def GET(self):
        session = web.config._session
        id_infante = session.id_infante_actual

        conn = sqlite3.connect("sql/conaap.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT puntaje, nivel_riesgo, fecha FROM resultados
            WHERE id_infante1 = ?
            ORDER BY fecha DESC, id_resultado DESC
            LIMIT 1
        """, (id_infante,))
        resultado = cur.fetchone()
        conn.close()

        if not resultado:
            raise web.HTTPError('303 See Other', {'Location': '/padre/inicio'})

        return render.resultado_padre(resultado)