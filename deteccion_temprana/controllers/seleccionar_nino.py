import web
import sqlite3

render = web.template.render('deteccion_temprana/views/')


class SeleccionarNino:
    def GET(self):
        session = web.config._session
        id_padres = session.id_referencia

        conn = sqlite3.connect("sql/conaap.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id_infante, nombre, edad FROM infantes WHERE id_padres = ?", (id_padres,))
        ninos = cur.fetchall()
        conn.close()

        return render.seleccionar_nino(ninos)


class ElegirNino:
    def GET(self):
        session = web.config._session
        datos = web.input(id_infante=None)

        session.id_infante_actual = int(datos.id_infante)

        raise web.HTTPError('303 See Other', {'Location': '/padre/inicio'})