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

class DocentesAdmin:
    def GET(self):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM docentes ORDER BY id DESC")
        docentes = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total FROM docentes")
        total = cursor.fetchone()['total']

        conn.close()
        return render.docentes(docentes=docentes, total=total)
    
class NuevoDocenteAdmin:
    def GET(self):
        return render.nuevo_docente()

    def POST(self):
        data = web.input(nombre='', correo='', clave='')
        nombre = data.get('nombre')
        correo = data.get('correo')
        clave = data.get('clave')
        alumnos = 0  # Inicia con 0 alumnos registrados

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO docentes (nombre, correo, clave, alumnos) VALUES (?, ?, ?, ?)",
            (nombre, correo, clave, alumnos)
        )
        conn.commit()
        conn.close()

        raise web.seeother('/administrativo/docentes')