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

        # Consultar contadores reales de las tablas
        cursor.execute("SELECT COUNT(*) as total FROM alumnos")
        total_alumnos = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM docentes")
        total_docentes = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM padres")
        total_padres = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM estrategias_didacticas")
        total_estrategias = cursor.fetchone()['total']

        conn.close()

        return render.inicio(
            total_alumnos=total_alumnos,
            total_docentes=total_docentes,
            total_padres=total_padres,
            total_estrategias=total_estrategias
        )