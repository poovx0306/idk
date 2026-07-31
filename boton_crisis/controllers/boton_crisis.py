import web
import sqlite3
import datetime

render = web.template.render('boton_crisis/views')


class BotonCrisis:
    """Muestra el protocolo de crisis y registra cuando se marca como atendida."""

    def GET(self):
        datos = web.input(id="1")
        id_docente = datos.id
        return render.boton_crisis(id_docente)

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
    """Pantalla de confirmación con la palomita verde (acceso directo, por si acaso)."""

    def GET(self):
        datos = web.input(id="1")
        id_docente = datos.id
        return render.confirmacion(id_docente, "")