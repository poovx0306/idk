import web
import sqlite3
import os

render = web.template.render('administrativos/views/')

def conectar_bd():
    conn = sqlite3.connect('sql/conaap.db')
    conn.row_factory = sqlite3.Row
    return conn

class Resultados:
    def GET(self):
        data = web.input(riesgo='', cuestionario='', buscar='')
        riesgo = data.get('riesgo', '').strip()
        cuestionario = data.get('cuestionario', '').strip()
        buscar = data.get('buscar', '').strip()

        conn = conectar_bd()
        cursor = conn.cursor()

        query = """
            SELECT i.nombre AS alumno, c.titulo AS cuestionario,
                   r.puntaje, r.nivel_riesgo
            FROM resultados r
            JOIN infantes i ON r.id_infante1 = i.id_infante
            LEFT JOIN cuestionarios c ON c.estado = 'Activo'
            WHERE 1=1
        """
        params = []

        if buscar:
            query += " AND LOWER(i.nombre) LIKE LOWER(?)"
            params.append(f"%{buscar}%")

        if riesgo:
            query += " AND LOWER(r.nivel_riesgo) = LOWER(?)"
            params.append(riesgo)

        if cuestionario:
            query += " AND LOWER(c.titulo) LIKE LOWER(?)"
            params.append(f"%{cuestionario}%")

        query += " ORDER BY r.id_resultado DESC"

        cursor.execute(query, params)
        resultados = cursor.fetchall()

        conn.close()

        return render.resultados(resultados=resultados, riesgo_sel=riesgo, cuestionario_sel=cuestionario, buscar_sel=buscar)