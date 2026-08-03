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

class InicioAdministrativo:
    def GET(self):
        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM alumnos")
        total_alumnos = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM docentes")
        total_docentes = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM resultados_cuestionarios")
        total_cuestionarios = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM estrategias_didacticas")
        total_estrategias = cursor.fetchone()['total']

        cursor.execute("""
            SELECT alumno as nombre_completo, 
                   puntaje, cuestionario as tipo_cuestionario, 
                   nivel_riesgo, fecha 
            FROM resultados_cuestionarios 
            ORDER BY fecha DESC LIMIT 5
        """)
        casos_pendientes = cursor.fetchall()

        conn.close()

        return render.inicio(
            total_alumnos=total_alumnos,
            total_docentes=total_docentes,
            total_cuestionarios=total_cuestionarios,
            total_estrategias=total_estrategias,
            casos_pendientes=casos_pendientes
        )