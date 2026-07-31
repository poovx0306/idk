import web
import sqlite3
import datetime

render = web.template.render('deteccion_temprana/views/')


class DeteccionTemprana:
    def GET(self):
        session = web.config._session
        es_padre = bool(getattr(session, "id_infante_actual", None))
        return render.cuestionario(es_padre)

    def POST(self):
        datos = web.input()
        sesion = web.config._session

        puntuacion = 0
        for clave, valor in datos.items():
            if valor == "a_veces":
                puntuacion += 1
            elif valor == "raro":
                puntuacion += 2

        if puntuacion < 15:
            nivel_riesgo = "Bajo"
        elif puntuacion < 30:
            nivel_riesgo = "Medio"
        else:
            nivel_riesgo = "Alto"

        id_infante = getattr(sesion, "id_infante_actual", None)

        if id_infante:
            conexion = sqlite3.connect("sql/conaap.db")
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO resultados (puntaje, fecha, nivel_riesgo, numero_de_especialista, id_infante1) VALUES (?, ?, ?, ?, ?)",
                (puntuacion, datetime.date.today().isoformat(), nivel_riesgo, "Pendiente de asignar", id_infante)
            )
            conexion.commit()
            conexion.close()
            raise web.HTTPError('303 See Other', {'Location': '/padre/resultado'})

        return render.resultado(puntuacion)