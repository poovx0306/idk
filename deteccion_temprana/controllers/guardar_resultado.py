import web
import sqlite3
import json
from datetime import date

render = web.template.render('deteccion_temprana/views/')


class GuardarResultadoAPI:
    def POST(self):
        session = web.config._session
        id_infante = session.id_infante_actual

        try:
            datos = json.loads(web.data())
            puntaje = int(datos.get("puntaje", 0))
        except Exception:
            web.header('Content-Type', 'application/json')
            return json.dumps({"ok": False})

        if puntaje < 15:
            nivel_riesgo = "Bajo"
        elif puntaje < 30:
            nivel_riesgo = "Medio"
        else:
            nivel_riesgo = "Alto"

        conn = sqlite3.connect("sql/conaap.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO resultados (puntaje, fecha, nivel_riesgo, id_infante1) VALUES (?, ?, ?, ?)",
            (puntaje, str(date.today()), nivel_riesgo, id_infante)
        )
        conn.commit()
        conn.close()

        web.header('Content-Type', 'application/json')
        return json.dumps({"ok": True})