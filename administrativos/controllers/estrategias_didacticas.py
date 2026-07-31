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

class EstrategiasDidacticasAdmin:
    def GET(self):
        data = web.input(materia='', grado='')
        materia = data.get('materia', '').strip()
        grado = data.get('grado', '').strip()

        conn = conectar_bd()
        cursor = conn.cursor()

        query = "SELECT * FROM estrategias_didacticas WHERE 1=1"
        params = []

        if materia:
            query += " AND LOWER(materia) = LOWER(?)"
            params.append(materia)

        if grado:
            query += " AND grado = ?"
            params.append(grado)

        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        estrategias = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM estrategias_didacticas")
        total_estrategias = cursor.fetchone()['total']

        conn.close()
        return render.estrategias_didacticas(
            estrategias=estrategias, 
            total=total_estrategias,
            materia_sel=materia, 
            grado_sel=grado
        )

class NuevaEstrategiaAdmin:
    def GET(self):
        return render.nueva_estrategia()

    def POST(self):
        data = web.input(titulo='', condicion='', materia='', grado='', objetivo='', materiales='', pasos='', accion='Publicar')
        
        titulo = data.get('titulo')
        materia = data.get('materia')
        grado = data.get('grado')
        estado = 'Publicada' if data.get('accion') == 'Publicar' else 'Borrador'

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO estrategias_didacticas (titulo, materia, grado, estado) VALUES (?, ?, ?, ?)",
            (titulo, materia, grado, estado)
        )
        conn.commit()
        conn.close()

        raise web.seeother('/administrativo/estrategias')