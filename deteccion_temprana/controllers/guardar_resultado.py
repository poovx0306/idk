import web
import sqlite3
import json
import datetime


class GuardarResultadoAPI:
    def POST(self):
        session = web.config._session
        id_infante = getattr(session, "id_infante_actual", None)

        web.header('Content-Type', 'application/json')

        if not id_infante:
            return json.dumps({"ok": False, "error": "No hay sesion de padre activa"})

        datos = json.loads(web.data())
        puntaje = int(datos.get("puntaje", 0))

        if puntaje < 15:
            nivel_riesgo = "Bajo"
        elif puntaje < 30:
            nivel_riesgo = "Medio"
        else:
            nivel_riesgo = "Alto"

        conexion = sqlite3.connect("sql/conaap.db")
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO resultados (puntaje, fecha, nivel_riesgo, numero_de_especialista, id_infante1) VALUES (?, ?, ?, ?, ?)",
            (puntaje, datetime.date.today().isoformat(), nivel_riesgo, "Pendiente de asignar", id_infante)
        )
        conexion.commit()
        conexion.close()

        return json.dumps({"ok": True})