import web
import sqlite3
import json
from datetime import date

render = web.template.render('deteccion_temprana/views/')

class GuardarResultadoAPI:
    def POST(self):
        session = web.config._session
        id_infante = session.id_infante_actual

        web.header('Content-Type', 'application/json')

        if not id_infante:
            return json.dumps({"ok": False, "error": "no_hay_infante_seleccionado"})

        try:
            datos = json.loads(web.data())
            puntaje = int(datos.get("puntaje", 0))
        except Exception:
            return json.dumps({"ok": False, "error": "datos_invalidos"})

        print("DATOS RECIBIDOS:", datos)
        print("PUNTAJE CONVERTIDO:", puntaje)

        if puntaje >= 35:
            nivel_riesgo = "Alto"
        elif puntaje >= 18:
            nivel_riesgo = "Medio"
        else:
            nivel_riesgo = "Bajo"

        try:
            conn = sqlite3.connect("sql/conaap.db")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO resultados (puntaje, fecha, nivel_riesgo, numero_de_especialista, id_infante1) VALUES (?, ?, ?, ?, ?)",
                (puntaje, str(date.today()), nivel_riesgo, "Pendiente de asignar", id_infante)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

        return json.dumps({"ok": True})