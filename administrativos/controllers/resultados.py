import web
import sqlite3
import os

render = web.template.render('administrativos/views/')

def conectar_bd():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'sql', 'conaap.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

class Resultados:
    def GET(self):
        data = web.input(riesgo='', cuestionario='')
        riesgo = data.get('riesgo', '').strip()
        cuestionario = data.get('cuestionario', '').strip()

        conn = conectar_bd()
        cursor = conn.cursor()

        query = "SELECT * FROM resultados_cuestionarios WHERE 1=1"
        params = []

        if riesgo:
            query += " AND LOWER(nivel_riesgo) = LOWER(?)"
            params.append(riesgo)

        if cuestionario:
            query += " AND LOWER(cuestionario) LIKE LOWER(?)"
            params.append(f"%{cuestionario}%")

        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        resultados = cursor.fetchall()

        conn.close()
        return render.resultados(resultados=resultados, riesgo_sel=riesgo, cuestionario_sel=cuestionario)