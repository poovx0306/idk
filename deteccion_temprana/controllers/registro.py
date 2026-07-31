import web
import sqlite3

render = web.template.render('deteccion_temprana/views/')


class RegistroPrevio:
    def GET(self):
        return render.registro()

    def POST(self):
        datos = web.input(nombre="", primer_apellido="", edad="")
        sesion = web.config._session

        id_padres = sesion.id_referencia
        nombre_completo = ("%s %s" % (datos.nombre, datos.primer_apellido)).strip()

        try:
            edad = int(datos.edad)
        except ValueError:
            edad = 0

        conexion = sqlite3.connect("sql/conaap.db")
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO infantes (nombre, edad, id_docente1, id_padres) VALUES (?, ?, ?, ?)",
            (nombre_completo, edad, 1, id_padres)
        )
        id_infante = cursor.lastrowid
        conexion.commit()
        conexion.close()

        sesion.id_infante_actual = id_infante

        raise web.HTTPError('303 See Other', {'Location': '/padre/inicio'})