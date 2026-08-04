import web
import sqlite3
import datetime

render = web.template.render('boton_crisis/views')


def obtener_docente(cursor, id_docente):
    cursor.execute(
        "SELECT nombre, correo FROM docente WHERE id_docente = ?",
        (id_docente,),
    )
    fila = cursor.fetchone()
    nombre = fila["nombre"] if fila else "Docente"
    correo = fila["correo"] if fila else "sin-correo@conafe.gob.mx"
    return nombre, correo


class BotonCrisis:
    def GET(self):
        datos = web.input(id="1")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        nombre_docente, correo_docente = obtener_docente(cursor, id_docente)
        conexion.close()

        return render.boton_crisis(id_docente, nombre_docente, correo_docente)

    def POST(self):
        datos = web.input(id="1", notas="")
        id_docente = datos.id
        notas = datos.notas.strip()

        conexion = sqlite3.connect("sql/conaap.db")
        cursor = conexion.cursor()

        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO crisis_atendida (id_docente, fecha_hora, notas) VALUES (?, ?, ?)",
            (id_docente, ahora, notas),
        )
        conexion.commit()
        conexion.close()

        return render.confirmacion(id_docente, notas)


class ConfirmacionCrisis:
    def GET(self):
        datos = web.input(id="1")
        id_docente = datos.id
        return render.confirmacion(id_docente, "")