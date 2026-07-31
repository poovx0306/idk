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

class AlumnosAdmin:
    def GET(self):
        data = web.input(docente='', grado='')
        docente = data.get('docente', '').strip()
        grado = data.get('grado', '').strip()

        conn = conectar_bd()
        cursor = conn.cursor()

        query = "SELECT * FROM alumnos WHERE 1=1"
        params = []

        if docente:
            query += " AND docente_asignado = ?"
            params.append(docente)

        if grado:
            query += " AND grado = ?"
            params.append(grado)

        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        alumnos = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total FROM alumnos")
        total = cursor.fetchone()['total']

        conn.close()
        return render.alumnos(
            alumnos=alumnos, 
            total=total, 
            docente_sel=docente, 
            grado_sel=grado
        )
    
class NuevoAlumnoAdmin:
    def GET(self):
        return render.nuevo_alumno()

    def POST(self):
        data = web.input(nombre='', edad='', condicion='', docente_asignado='', grado='')
        
        nombre = data.get('nombre')
        edad = data.get('edad')
        condicion = data.get('condicion')
        docente_asignado = data.get('docente_asignado')
        grado = data.get('grado')

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alumnos (nombre, edad, condicion, docente_asignado, grado) VALUES (?, ?, ?, ?, ?)",
            (nombre, edad, condicion, docente_asignado, grado)
        )
        conn.commit()
        conn.close()

        raise web.seeother('/administrativo/alumnos')