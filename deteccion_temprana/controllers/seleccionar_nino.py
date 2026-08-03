import web
import sqlite3

render = web.template.render('deteccion_temprana/views/')


class SeleccionarNino:
    def GET(self):
        sesion = web.config._session
        id_padres = sesion.id_referencia

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        cursor.execute("SELECT id_infante, nombre, edad FROM infantes WHERE id_padres = ?", (id_padres,))
        ninos = cursor.fetchall()
        conexion.close()

        return render.seleccionar_nino(ninos)


class ElegirNino:
    def GET(self):
        datos = web.input(id_infante="")
        sesion = web.config._session
        sesion.id_infante_actual = datos.id_infante
        raise web.HTTPError('303 See Other', {'Location': '/padre/inicio'})